from prometheus_client import (
    Counter,
    Gauge,
    start_http_server,
)
import random
import requests
import time


class Prober:
    _url = 'http://oncall:8080/users'

    def __init__(self):
        self._succesfull_requests = Counter('oncall_prober_successful', 'Oncall-prober successful requests')
        self._failed_requests = Counter('oncall_prober_failed', 'Oncall-prober failed requests')
        self._request_duration_ms = Gauge('oncall_prober_request_duration_ms', 'Oncall-prober request duration in ms')

    def probe(self):
        probe_failed = False
        username = f'test_user_{random.randint(1, 10)}'

        start_probe = time.perf_counter()
        try:
            create_user_response = requests.post(f'{self._url}/users', json={'name': username})
            if create_user_response.status_code // 100 != 2:
                raise Exception('Bad status code, probe failed')
        except:
            probe_failed = True

        if not probe_failed:
            try:
                delete_user_response = requests.delete(f'{self._url}/{username}')
                if delete_user_response.status_code // 100 != 2:
                    raise Exception('Bad status code, probe failed')
            except:
                probe_failed = True
        
        duration = time.perf_counter() - start_probe    # returns seconds float
        if probe_failed:
            self._failed_requests.inc()
        else:
            self._succesfull_requests.inc()
        self._request_duration_ms.set(duration * 1000)


if __name__ == "__main__":
    prober = Prober()
    start_http_server(8081)

    while True:
        prober.probe()
        time.sleep(5)
