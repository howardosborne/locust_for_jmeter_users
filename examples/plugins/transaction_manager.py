from locust import events
from time import time
from datetime import datetime
from itertools import groupby


class TransactionManager:
    def __init__(self):
        self.transaction_count = 0
        self.transactions = {}
        self.flat_transaction_list = []
        self.completed_transactions = {}
        self.field_delimiter = ","
        self.row_delimiter = "\n"
        self.timestamp_format = "%Y-%m-%d %H:%M:%S"
        self.flush_size = 100
        # results filename format
        self.transactions_filename = f'transactions_{datetime.fromtimestamp(time()).strftime("%Y_%m_%d_%H_%M_%S")}.csv'

        # fields set by default in jmeter
        self.csv_headers = [
            "start_time",
            "duration",
            "transaction_name",
            "user_count",
            "success",
            "failure_message"
        ]
        self.user_count = 0
        events.init.add_listener(self._on_locust_init)
        events.init_command_line_parser.add_listener(self.command_line_parser)
        events.quitting.add_listener(self._write_final_log)

    def command_line_parser(self, parser):
        parser.add_argument(
            "--log_transactions_in_file",
            help="log transactions in file rather than using the web ui",
            default=False,
        )

    def start_transaction(self, transaction_name):
        self.transaction_count += 1
        # using the transaction_count as a unique identifier
        transaction_id = self.transaction_count
        now = time()
        # Transaction(transaction_id, transaction_name, now)
        transaction = {}
        transaction["transaction_id"] = transaction_id
        transaction["transaction_name"] = transaction_name
        transaction["start_time"] = now
        transaction["end_time"] = None
        transaction["duration"] = None
        transaction["success"] = None
        transaction["failure_message"] = None
        transaction["user_count"] = self.runner.user_count
        self.transactions[transaction_id] = transaction
        return transaction_id

    def end_transaction(self, transaction_id, success=True, failure_message=""):
        # completes the transction
        now = time()
        t = self.transactions[transaction_id]
        t["end_time"] = now
        start_time = t["start_time"]
        t["duration"] = now - start_time
        t["success"] = success
        t["failure_message"] = failure_message
        # format to add to a flat results file
        csv_row = f'{datetime.fromtimestamp(t["start_time"]).strftime(self.timestamp_format)}{self.field_delimiter}{round(t["duration"],2)}{self.field_delimiter}{t["transaction_name"]}{self.field_delimiter}{t["user_count"]}{self.field_delimiter}{t["success"]}{self.field_delimiter}{t["failure_message"]}'
        self.flat_transaction_list.append(csv_row)

        if t["transaction_name"] in self.completed_transactions:
            self.completed_transactions[t["transaction_name"]].append(t)
        else:
            self.completed_transactions[t["transaction_name"]] = []
            self.completed_transactions[t["transaction_name"]].append(t)

        del self.transactions[transaction_id]
        if len(self.flat_transaction_list) >= self.flush_size:
            if self.log_transactions_in_file:
                self._flush_to_log()

    def _create_results_log(self):
        results_file = open(self.transactions_filename, "w")
        results_file.write(
            self.field_delimiter.join(self.csv_headers) + self.row_delimiter
        )
        results_file.flush()
        return results_file

    def _flush_to_log(self):
        self.results_file.write(
            self.row_delimiter.join(self.flat_transaction_list) + self.row_delimiter
        )
        self.results_file.flush()
        self.flat_transaction_list = []

    def _write_final_log(self, **kwargs):
        if self.log_transactions_in_file:
            self.results_file.write(
                self.row_delimiter.join(self.flat_transaction_list) + self.row_delimiter
            )
            self.results_file.close()

    def _on_locust_init(self, environment, runner, **kwargs):
        self.env = environment
        self.runner = runner
        # determine whether to ouput to file
        self.log_transactions_in_file = self.env.parsed_options.log_transactions_in_file
        if self.log_transactions_in_file:
            self.results_file = self._create_results_log()
        if self.env.web_ui:
            # this route makes sense if a csv isn't being created on the fly
            @self.env.web_ui.app.route("/stats/transactions/all/csv")
            def transactions_results_page():
                file_name = f'all_transactions_{datetime.fromtimestamp(time()).strftime("%Y_%m_%d_%H_%M_%S")}.csv'
                disposition = f"attachment;filename={file_name}"
                headers = {}
                headers["Content-type"] = "text/csv"
                headers["Content-disposition"] = disposition
                response = self.env.web_ui.app.response_class(
                    response=self.field_delimiter.join(self.csv_headers)
                    + self.row_delimiter
                    + self.row_delimiter.join(self.flat_transaction_list),
                    headers=headers,
                    status=200,
                    mimetype="text/csv",
                )
                return response

            # provides summary stats like requests
            @self.env.web_ui.app.route("/stats/transactions/csv")
            def transactions_summary_page():
                # make some summaries from the transactions
                resp = []
                resp.append(
                    '"Name","Request Count","Median Response Time","Average Response Time","Min Response Time","Max Response Time"'
                )
                for tname in self.completed_transactions:
                    # for key, group in groupby(self.completed_transactions, lambda x: x["transaction_name"]):
                    durations = [
                        sub["duration"] for sub in self.completed_transactions[tname]
                    ]
                    sorted_durations = sorted(durations)
                    avg = round(sum(sorted_durations) / len(sorted_durations), 2)
                    resp.append(
                        f"{tname}{self.field_delimiter}{len(durations)}{self.field_delimiter}{avg}{self.field_delimiter}{round(sorted_durations[0],2)}{self.field_delimiter}{round(sorted_durations[-1],2)}"
                    )

                file_name = f'transactions_{datetime.fromtimestamp(time()).strftime("%Y_%m_%d_%H_%M_%S")}.csv'
                disposition = f"attachment;filename={file_name}"
                headers = {}
                headers["Content-type"] = "text/csv"
                headers["Content-disposition"] = disposition
                response = self.env.web_ui.app.response_class(
                    response=self.row_delimiter.join(resp),
                    headers=headers,
                    status=200,
                    mimetype="text/csv",
                )
                return response


# not sure if this will be useful but not taking it out yet...
# class Transaction:
#     def __init__(self, transaction_id, transaction_name, start_time, user_count=None):
#         self.transaction_id = transaction_id
#         self.transaction_name = transaction_name
#         self.start_time = start_time
#         self.user_count = user_count
#         self.end_time = None
#         self.duration = None
#         self.success = None
#         self.failure_message = None
