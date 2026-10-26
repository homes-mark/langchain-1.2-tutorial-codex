"""Python 3.12 stdlib. Boundary checks used before any model/tool side effects."""
from dataclasses import dataclass
import hashlib
import json
import sqlite3


@dataclass(frozen=True)
class Identity:
    tenant: str
    user: str
    can_read: bool


def lookup(db, identity, ticket_id):
    # Identity must come from verified server authentication, never model arguments.
    if not identity.can_read:
        raise PermissionError("DENIED")
    return db.execute("SELECT title FROM tickets WHERE tenant = ? AND owner = ? AND id = ?",
                      (identity.tenant, identity.user, ticket_id)).fetchone()


def demo():
    db = sqlite3.connect(":memory:")
    try:
        db.execute("CREATE TABLE tickets(tenant TEXT, owner TEXT, id TEXT, title TEXT)")
        db.executemany("INSERT INTO tickets VALUES(?,?,?,?)", [
            ("a", "alice", "T1", "VPN unavailable"), ("b", "bob", "T2", "Private incident")])
        actor = Identity("a", "alice", True)
        assert lookup(db, actor, "T1") == ("VPN unavailable",)
        assert lookup(db, actor, "T2") is None
        assert lookup(db, actor, "' OR 1=1 --") is None
        try:
            lookup(db, Identity("a", "alice", False), "T1")
        except PermissionError:
            pass
        else:
            raise AssertionError("permission must be enforced before query")
        # Allowlist fields. Hash below fingerprints a request ID, NOT personal information.
        event = {"event": "ticket_read", "request_hash": hashlib.sha256(b"request-demo-1").hexdigest()[:16], "result": "allowed"}
        print(json.dumps(event))
        print("PASS: tenant/owner isolation + permission + SQL parameterization")
    finally:
        db.close()


if __name__ == "__main__":
    demo()
