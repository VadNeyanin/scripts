import pytest
import allure

@allure.title("Package {package}")
@pytest.mark.parametrize('package, version', [
    ('cri-o', '1.35.2-1.1'),
    ('kubeadm', '1.35.4-1.1'),
    ('kubectl', '1.35.4-1.1'),
    ('kubelet', '1.35.4-1.1')
])
def test_pkg_version(host, package, version):
    with allure.step(f"Check package {package}"):
        pkg = host.package(package)
        assert pkg.version == version