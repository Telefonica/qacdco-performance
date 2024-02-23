import yaml
import re

class ConfigArgs:
    def __init__(self, yaml_config: dict):
        self.prometheus_url = self.validate_url(yaml_config["prometheus_url"])
        self.start_date = self.validate_int("start_date", yaml_config["start_date"])
        self.end_date = self.validate_int("end_date", yaml_config["end_date"])
        self.step = self.validate_int("interval", yaml_config["interval"])
        self.generate_graphs = self.validate_bool("generate_graphs", yaml_config["generate_graphs"])
        self.authentication = self.validate_auth(yaml_config["authentication"])
        self.metrics = self.validate_metrics(yaml_config["metrics"])
    
    def validate_url(self, arg_value, pat=re.compile(r"^https?://.+$")):
        if not pat.match(arg_value):
            raise yaml.YAMLError(f"prometheus_url: Invalid url value {arg_value}")
        return arg_value
    
    def validate_int(self, arg, value):
        if not isinstance(value, int):
            raise yaml.YAMLError(f"{arg}: Expected an integer, but got {type(value).__name__} instead.")
        return value
    
    def validate_bool(self, arg, value):
        if not isinstance(value, bool):
            raise yaml.YAMLError(f"{arg}: Expected a boolean, but got {type(value).__name__} instead.")
        return value
    
    def validate_user_pass(self, value):
        if len(value.split(':')) != 2:
            raise yaml.YAMLError("authentication: user_password must be in the format 'user:password'")
        return value

    def validate_auth(self, value):
        if not isinstance(value, list) or len(value) != 1:
            raise yaml.YAMLError("authentication: field must be a list with exactly one dict with keys \"type\" and \"credentials\")")
        
        auth_type = value[0].get("type")
        if not auth_type:
            raise yaml.YAMLError("authentication: missing 'type' key")
        
        credentials = value[0].get("credentials")
        if not credentials:
            raise yaml.YAMLError("authentication: missing 'credentials' key")
        
        if auth_type == "user_password":
            self.validate_user_pass(value[0]["credentials"])
        elif auth_type == "basic_auth":
            pass
        else:
            raise yaml.YAMLError(f"authentication: type {auth_type} not supported")
        
        return value
    
    def validate_metrics(self, metrics_list):
        if not isinstance(metrics_list, list):
            raise yaml.YAMLError(f"metrics: Expected a list, but got {type(metrics_list).__name__} instead.")
        required_keys = ["query", "metric_name", "y_axis_units"]
        for metric in metrics_list:
            if not isinstance(metric, dict):
                raise yaml.YAMLError(f"metrics: Each metric should be a dictionary, but got {type(metric).__name__} instead.")
            
            missing_keys = [key for key in required_keys if key not in metric]
            if missing_keys:
                raise yaml.YAMLError(f"metrics: Missing required keys {', '.join(missing_keys)} in a metric.")
            for key, value in metric.items():
                if not isinstance(value, str):
                    raise yaml.YAMLError(f"metrics: For key '{key}', expected a string, but got {type(value).__name__} instead.")

        return metrics_list
