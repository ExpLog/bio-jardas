from bio_jardas.exceptions import JardasError


class TimeGatedError(JardasError):
    def __init__(self, time_gate_name: str, user_snowflake_id: int):
        super().__init__(
            f"Feature {time_gate_name} is time gated for user {user_snowflake_id}"
        )
        self.time_gate_name = time_gate_name
        self.user_snowflake_id = user_snowflake_id
