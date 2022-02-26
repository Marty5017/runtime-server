#! /usr/bin/env python3
"""
Handles the storage of application data.

This implementation makes use of a simple SQLite database, but it can easily
be replaced by a different database without changing this interface

TODO: Replace SQLite with a more performant database
"""

# pylint: disable=broad-except


# default modules
import datetime
import sqlite3
from sqlite3 import Error
from typing import Union

# custom modules
import logger as Logger


class Storage:
    """
    This class manages the connection with the database system
    """

    def __init__(self, filename: str = "jobs.db") -> None:
        """
        Initialse database config
        """
        self.db_file = filename
        self.connection = None

    def connect_to_db(self):
        """
        Create a connection to the database
        """
        try:
            self.connection = sqlite3.connect(
                self.db_file,
                check_same_thread=False
            )

        except Error as err:
            Logger.log_exception("DB error connecting to DB", err)

        except Exception as exe:
            Logger.log_exception("Connect to DB exception", exe)

    def create_job_table(self) -> bool:
        """
        Create the job table if it doesn't exist yet
        """
        sql_create_table = (
            "CREATE TABLE IF NOT EXISTS jobs ("
            "   id INTEGER PRIMARY KEY,"
            "   job TEXT NOT NULL,"
            "   mode TEXT,"
            "   status TEXT,"
            "   runtime INTEGER,"
            "   return_code INTEGER,"
            "   runtime_error TEXT,"
            "   created_time TEXT,"
            "   start_time TEXT,"
            "   end_time TEXT"
            "); "
        )
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql_create_table)
            return True

        except Error as err:
            Logger.log_exception("DB error creating the job table", err)

        except Exception as exe:
            Logger.log_exception("Create job table in DB exception", exe)

        # return False on error
        return False

    def add_job(self, job: str, mode: str) -> int:
        """
        Add a new job to the job table
        """
        try:
            created_time = datetime.datetime.utcnow().isoformat()
            if not self.connection:
                self.connect_to_db()
            self.create_job_table()

            sql_insert = (
                " INSERT INTO"
                "    jobs (job, mode, status, created_time)"
                " VALUES"
                "    (?,?,?,?)"
            )

            cursor = self.connection.cursor()
            cursor.execute(
                sql_insert,
                [job, mode, "Scheduled", created_time]
            )
            self.connection.commit()
            return cursor.lastrowid

        except Error as err:
            Logger.log_exception("DB error when creating job", err)

        except Exception as exe:
            Logger.log_exception("Create job entry in DB exception", exe)

        # return 0 on error
        return 0

    # disable this warning because this method will be an exception to the rule
    # if any other arguments need to be added we'll need to refactor to use
    # fewer arguments
    # pylint: disable=too-many-arguments
    def update_job(
        self,
        db_id: int,
        status: str,
        runtime: Union[None, int] = None,
        return_code: Union[None, int] = None,
        runtime_error: Union[None, str] = None
    ) -> int:
        """
        Update a job from the job table
        """
        try:
            timestamp = timestamp = datetime.datetime.utcnow().isoformat()

            if not self.connection:
                self.connect_to_db()

            time_field = 'start_time' if return_code is None else 'end_time'
            sql_update = (
                " UPDATE"
                "    jobs"
                " SET"
                "    status = ?,"
                "    runtime = ?,"
                "    return_code = ?,"
                "    runtime_error = ?,"
                f"   {time_field} = ?"
                " WHERE"
                "    id = ?"
            )

            cursor = self.connection.cursor()
            cursor.execute(
                sql_update,
                [status, runtime, return_code, runtime_error, timestamp, db_id]
            )
            self.connection.commit()
            return cursor.lastrowid

        except Error as err:
            Logger.log_exception(f"DB error when updating job {db_id}", err)

        except Exception as exe:
            Logger.log_exception(
                f"Update job {db_id} entry in DB exception",
                exe
            )

        # return 0 on error
        return 0

    def get_job(self, db_id: int) -> dict:
        """
        Retrieve a job from the job table
        """
        try:
            if not self.connection:
                self.connect_to_db()

            sql_select = (
                " SELECT"
                "    *"
                " FROM"
                "    jobs"
                " WHERE"
                "    id = ?"
            )

            cursor = self.connection.cursor()
            cursor.execute(sql_select, [db_id])
            self.connection.commit()
            row = cursor.fetchone()
            return {
                "id": row[0],
                "job": row[1],
                "mode": row[2],
                "status": row[3],
                "runtime": row[4],
                "return_code": row[5],
                "runtime_error": row[6],
                "created_time": row[7],
                "start_time": row[8],
                "end_time": row[9],
            }

        except Error as err:
            Logger.log_exception(
                f"DB error when selecting job {db_id} from DB",
                err
            )

        except Exception as exe:
            Logger.log_exception(
                f"Select job {db_id} from DB exception",
                exe
            )

        # return 0 on error
        return 0

    def list_jobs(self) -> list:
        """
        Retrieve a list of all jobs in the DB
        """
        try:
            if not self.connection:
                self.connect_to_db()

            sql_select = (
                " SELECT"
                "    *"
                " FROM"
                "    jobs"
                " ORDER BY id ASC"
            )

            cursor = self.connection.cursor()
            cursor.execute(sql_select)
            self.connection.commit()
            return_list = []
            for row in cursor.fetchall():
                return_list.append({
                    "id": row[0],
                    "job": row[1],
                    "mode": row[2],
                    "status": row[3],
                    "runtime": row[4],
                    "return_code": row[5],
                    "runtime_error": row[6],
                    "created_time": row[7],
                    "start_time": row[8],
                    "end_time": row[9],
                })
            return return_list

        except Error as err:
            Logger.log_exception(
                "DB error when listing all DB",
                err
            )

        except Exception as exe:
            Logger.log_exception(
                "List all jobs in DB exception",
                exe
            )

        # return 0 on error
        return 0


STORAGE_INSTANCE = Storage()
