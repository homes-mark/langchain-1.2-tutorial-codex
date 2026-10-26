"""无密钥回归：控制流、ACL、审批拒绝/批准、事务幂等。依赖 requirements.lock.txt。"""
from dataclasses import replace
from contextlib import closing
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory

from helpdesk import (RequestContext, conversation_config, init_database,
                      lookup_ticket, retrieve, run_stage, write_ticket)


def main():
    for stage in range(1, 5):
        run = run_stage(stage)
        assert run["tickets"] == 0 and run["audit"] == 0
    pending = run_stage(5)
    assert pending["result"].get("__interrupt__") and pending["tickets"] == 0
    rejected = run_stage(5, decision="reject")
    assert rejected["tickets"] == rejected["audit"] == 0
    approved = run_stage(5, decision="approve")
    assert approved["tickets"] == approved["audit"] == 1
    with TemporaryDirectory() as directory:
        ctx = RequestContext("acme", "alice", ("requester",), "req-001",
                             str(Path(directory) / "test.sqlite3"))
        init_database(ctx.db_path)
        assert lookup_ticket("IT-2001", ctx) == {"error": "NOT_FOUND_OR_FORBIDDEN"}
        assert lookup_ticket("IT-1001", replace(ctx, user_id="mallory")) == {
            "error": "NOT_FOUND_OR_FORBIDDEN"}
        assert [x["source"] for x in retrieve("VPN", ctx)] == ["KB-001"]
        assert retrieve("不存在的关键词", ctx) == []
        assert conversation_config(ctx) != conversation_config(replace(ctx, tenant_id="globex"))
        first = write_ticket("VPN 失败", ctx)
        again = write_ticket("VPN 失败", ctx)
        assert first["created"] and not again["created"]
        assert first["ticket_id"] == again["ticket_id"]
        try:
            write_ticket("另一项请求", ctx)
        except ValueError:
            pass
        else:
            raise AssertionError("同幂等键不同内容必须拒绝")
        try:
            write_ticket("不应写入", replace(ctx, roles=(), request_id="req-002"))
        except PermissionError:
            pass
        else:
            raise AssertionError("无建单权限必须拒绝")
        with closing(sqlite3.connect(ctx.db_path)) as connection:
            assert connection.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] == 1
            assert connection.execute("SELECT COUNT(*) FROM audit").fetchone()[0] == 1
    print("PASS：5 阶段、审批、ACL、事务幂等边界通过")


if __name__ == "__main__":
    main()
