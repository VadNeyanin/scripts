import pytest
import allure

@allure.title("Services {service}")
@pytest.mark.parametrize('service', ['crio', 'kubelet'])
def test_services(host, service):
    with allure.step(f"service {service}"):
        srv = host.service(service)
        assert srv.is_valid