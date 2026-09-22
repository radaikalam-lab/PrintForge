import sqlite3
import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime, UTC
from persistence.interfaces import PrintJobRepository, PrinterRepository, ExecutionRepository
from domain.job import PrintJob, PrintJobState
from domain.printer import Printer, PrinterState
from domain.execution import PrintExecution, ExecutionState


def _row_to_print_job(row: Dict[str, Any]) -> PrintJob:
    return PrintJob(
        job_id=row["job_id"],
        source_document=row["source_document"],
        document_format=row["document_format"],
        requested_printer=row.get("requested_printer"),
        resolved_printer=row.get("resolved_printer"),
        media=row.get("media"),
        page_size=row.get("page_size"),
        orientation=row.get("orientation"),
        copies=row.get("copies", 1),
        duplex=bool(row.get("duplex", 0)),
        color_mode=row.get("color_mode"),
        resolution=row.get("resolution"),
        scaling=row.get("scaling"),
        page_range=row.get("page_range"),
        priority=row.get("priority", 0),
        submission_time=datetime.fromisoformat(row["submission_time"]) if row.get("submission_time") else datetime.now(UTC),
        requested_by=row.get("requested_by"),
        policy_context=json.loads(row["policy_context"]) if row.get("policy_context") else {},
        state=PrintJobState(row.get("state", "CREATED")),
        provenance=json.loads(row["provenance"]) if row.get("provenance") else {},
    )


def _row_to_printer(row: Dict[str, Any]) -> Printer:
    from domain.capabilities import PrinterCapabilities
    caps_data = json.loads(row["capabilities"]) if row.get("capabilities") else {}
    capabilities = PrinterCapabilities(**caps_data)
    return Printer(
        printer_id=row["printer_id"],
        name=row["name"],
        identity=row["identity"],
        protocol=row["protocol"],
        capabilities=capabilities,
        state=PrinterState(row.get("state", "UNKNOWN")),
        location=row.get("location"),
        provider=row.get("provider"),
        last_observation=json.loads(row["last_observation"]) if row.get("last_observation") else None,
        provenance=json.loads(row["provenance"]) if row.get("provenance") else {},
    )


class SQLitePrintJobRepository(PrintJobRepository):
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS print_jobs (
                    job_id TEXT PRIMARY KEY,
                    source_document TEXT NOT NULL,
                    document_format TEXT NOT NULL,
                    requested_printer TEXT,
                    resolved_printer TEXT,
                    media TEXT,
                    page_size TEXT,
                    orientation TEXT,
                    copies INTEGER DEFAULT 1,
                    duplex INTEGER DEFAULT 0,
                    color_mode TEXT,
                    resolution TEXT,
                    scaling TEXT,
                    page_range TEXT,
                    priority INTEGER DEFAULT 0,
                    submission_time TEXT,
                    requested_by TEXT,
                    policy_context TEXT,
                    state TEXT DEFAULT 'CREATED',
                    provenance TEXT
                )
            """)
            conn.commit()
        finally:
            conn.close()

    async def save(self, job: PrintJob) -> None:
        conn = self._get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO print_jobs (
                    job_id, source_document, document_format, requested_printer, resolved_printer,
                    media, page_size, orientation, copies, duplex, color_mode, resolution, scaling,
                    page_range, priority, submission_time, requested_by, policy_context, state, provenance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.job_id,
                    job.source_document,
                    job.document_format,
                    job.requested_printer,
                    job.resolved_printer,
                    job.media,
                    job.page_size,
                    job.orientation,
                    job.copies,
                    int(job.duplex),
                    job.color_mode,
                    job.resolution,
                    job.scaling,
                    job.page_range,
                    job.priority,
                    job.submission_time.isoformat(),
                    job.requested_by,
                    json.dumps(job.policy_context),
                    job.state.value,
                    json.dumps(job.provenance),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    async def get(self, job_id: str) -> Optional[PrintJob]:
        conn = self._get_connection()
        try:
            row = conn.execute("SELECT * FROM print_jobs WHERE job_id = ?", (job_id,)).fetchone()
            if row:
                return _row_to_print_job(dict(row))
            return None
        finally:
            conn.close()

    async def list(self) -> List[PrintJob]:
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT * FROM print_jobs").fetchall()
            return [_row_to_print_job(dict(row)) for row in rows]
        finally:
            conn.close()

    async def delete(self, job_id: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.execute("DELETE FROM print_jobs WHERE job_id = ?", (job_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()


class SQLitePrinterRepository(PrinterRepository):
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS printers (
                    printer_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    identity TEXT NOT NULL,
                    protocol TEXT NOT NULL,
                    capabilities TEXT,
                    state TEXT DEFAULT 'UNKNOWN',
                    location TEXT,
                    provider TEXT,
                    last_observation TEXT,
                    provenance TEXT
                )
            """)
            conn.commit()
        finally:
            conn.close()

    async def save(self, printer: Printer) -> None:
        conn = self._get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO printers (
                    printer_id, name, identity, protocol, capabilities, state, location, provider, last_observation, provenance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    printer.printer_id,
                    printer.name,
                    printer.identity,
                    printer.protocol,
                    json.dumps(printer.capabilities.model_dump()),
                    printer.state.value,
                    printer.location,
                    printer.provider,
                    json.dumps(printer.last_observation) if printer.last_observation else None,
                    json.dumps(printer.provenance),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    async def get(self, printer_id: str) -> Optional[Printer]:
        conn = self._get_connection()
        try:
            row = conn.execute("SELECT * FROM printers WHERE printer_id = ?", (printer_id,)).fetchone()
            if row:
                return _row_to_printer(dict(row))
            return None
        finally:
            conn.close()

    async def list(self) -> List[Printer]:
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT * FROM printers").fetchall()
            return [_row_to_printer(dict(row)) for row in rows]
        finally:
            conn.close()

    async def delete(self, printer_id: str) -> bool:
        conn = self._get_connection()
        try:
            cursor = conn.execute("DELETE FROM printers WHERE printer_id = ?", (printer_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()


class SQLiteExecutionRepository(ExecutionRepository):
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        conn = self._get_connection()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    execution_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    printer_id TEXT NOT NULL,
                    provider TEXT,
                    requested_operation TEXT NOT NULL,
                    accepted INTEGER DEFAULT 0,
                    timestamps TEXT,
                    provider_response TEXT,
                    execution_state TEXT DEFAULT 'PENDING',
                    failure_information TEXT,
                    provenance TEXT
                )
            """)
            conn.commit()
        finally:
            conn.close()

    async def save(self, execution: PrintExecution) -> None:
        conn = self._get_connection()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO executions (
                    execution_id, job_id, printer_id, provider, requested_operation, accepted,
                    timestamps, provider_response, execution_state, failure_information, provenance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    execution.execution_id,
                    execution.job_id,
                    execution.printer_id,
                    execution.provider,
                    execution.requested_operation,
                    int(execution.accepted),
                    json.dumps({k: v.isoformat() for k, v in execution.timestamps.items()}),
                    json.dumps(execution.provider_response) if execution.provider_response else None,
                    execution.execution_state.value,
                    json.dumps(execution.failure_information) if execution.failure_information else None,
                    json.dumps(execution.provenance),
                ),
            )
            conn.commit()
        finally:
            conn.close()

    async def get(self, execution_id: str) -> Optional[PrintExecution]:
        conn = self._get_connection()
        try:
            row = conn.execute("SELECT * FROM executions WHERE execution_id = ?", (execution_id,)).fetchone()
            if row:
                return self._row_to_execution(dict(row))
            return None
        finally:
            conn.close()

    async def list_by_job(self, job_id: str) -> List[PrintExecution]:
        conn = self._get_connection()
        try:
            rows = conn.execute("SELECT * FROM executions WHERE job_id = ?", (job_id,)).fetchall()
            return [self._row_to_execution(dict(row)) for row in rows]
        finally:
            conn.close()

    def _row_to_execution(self, row: Dict[str, Any]) -> PrintExecution:
        timestamps = {}
        if row.get("timestamps"):
            raw = json.loads(row["timestamps"])
            timestamps = {k: datetime.fromisoformat(v) for k, v in raw.items()}
        return PrintExecution(
            execution_id=row["execution_id"],
            job_id=row["job_id"],
            printer_id=row["printer_id"],
            provider=row.get("provider"),
            requested_operation=row["requested_operation"],
            accepted=bool(row.get("accepted", 0)),
            timestamps=timestamps,
            provider_response=json.loads(row["provider_response"]) if row.get("provider_response") else None,
            execution_state=ExecutionState(row.get("execution_state", "PENDING")),
            failure_information=json.loads(row["failure_information"]) if row.get("failure_information") else None,
            provenance=json.loads(row["provenance"]) if row.get("provenance") else {},
        )
