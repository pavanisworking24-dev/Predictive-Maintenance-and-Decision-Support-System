"""Idempotently create the three PROGNEX demo accounts.

Passwords are never hardcoded. Provide them through environment variables:

    PROGNEX_SEED_ADMIN_PASSWORD
    PROGNEX_SEED_MANAGER_PASSWORD
    PROGNEX_SEED_ENGINEER_PASSWORD

or run interactively and enter them when prompted:

    cd backend && python -m app.db.seed

Existing accounts (matched by email) are left untouched, so the command is
safe to run repeatedly.
"""

import getpass
import os
import sys
import uuid
from collections.abc import Callable, Mapping
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User

MIN_PASSWORD_LENGTH = 10


@dataclass(frozen=True)
class DemoAccount:
    key: str
    email: str
    name: str
    role: str

    @property
    def env_var(self) -> str:
        return f"PROGNEX_SEED_{self.key}_PASSWORD"


DEMO_ACCOUNTS: tuple[DemoAccount, ...] = (
    DemoAccount("ADMIN", "admin@prognex.com", "PROGNEX Admin", "ADMIN"),
    DemoAccount("MANAGER", "manager@prognex.com", "PROGNEX Manager", "MAINTENANCE_MANAGER"),
    DemoAccount("ENGINEER", "engineer@prognex.com", "PROGNEX Engineer", "MAINTENANCE_ENGINEER"),
)


class SeedError(RuntimeError):
    pass


def resolve_passwords(
    env: Mapping[str, str],
    prompt: Callable[[str], str] | None = None,
    accounts: tuple[DemoAccount, ...] = DEMO_ACCOUNTS,
) -> dict[str, str]:
    """Return {email: password} from env vars, prompting for any missing one."""
    passwords: dict[str, str] = {}
    for account in accounts:
        password = env.get(account.env_var)
        if not password:
            if prompt is None:
                raise SeedError(f"Missing password: set {account.env_var}")
            password = prompt(f"Password for {account.email} ({account.role}): ")
        if len(password) < MIN_PASSWORD_LENGTH:
            raise SeedError(
                f"Password for {account.email} must be at least {MIN_PASSWORD_LENGTH} characters"
            )
        passwords[account.email] = password
    return passwords


def seed_demo_users(
    db: Session,
    passwords: Mapping[str, str],
    accounts: tuple[DemoAccount, ...] = DEMO_ACCOUNTS,
) -> dict[str, list[str]]:
    """Create missing demo accounts. Returns {"created": [...], "skipped": [...]}."""
    result: dict[str, list[str]] = {"created": [], "skipped": []}

    for account in accounts:
        exists = db.execute(
            select(User.id).where(func.lower(User.email) == account.email)
        ).scalar_one_or_none()

        if exists is not None:
            result["skipped"].append(account.email)
            continue

        password = passwords.get(account.email)
        if not password:
            raise SeedError(f"No password provided for {account.email}")

        db.add(
            User(
                id=uuid.uuid4(),
                name=account.name,
                email=account.email,
                password_hash=hash_password(password),
                role=account.role,
                is_active=True,
            )
        )
        result["created"].append(account.email)

    db.commit()
    return result


def main() -> int:
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        missing = [a for a in DEMO_ACCOUNTS if not os.environ.get(a.env_var)]
        existing = set(
            db.execute(
                select(func.lower(User.email)).where(
                    func.lower(User.email).in_([a.email for a in DEMO_ACCOUNTS])
                )
            ).scalars()
        )
        # Only ask for passwords of accounts that still need creating.
        needed = tuple(a for a in DEMO_ACCOUNTS if a.email not in existing)
        prompt = getpass.getpass if (missing and sys.stdin.isatty()) else None

        passwords = resolve_passwords(os.environ, prompt, needed)
        result = seed_demo_users(db, passwords)
    except SeedError as exc:
        print(f"Seed failed: {exc}", file=sys.stderr)
        return 1
    finally:
        db.close()

    for email in result["created"]:
        print(f"created  {email}")
    for email in result["skipped"]:
        print(f"exists   {email}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
