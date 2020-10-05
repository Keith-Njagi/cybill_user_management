import pytest

from app.user_functions.platform_fetcher import compute_platform_version

class TestComputePlatformVersion(object):

    def test_windows_platform(self):
        test_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        test_platform = 'windows'
        actual = compute_platform_version(test_agent, test_platform)
        expected = 'Windows NT 10.0'
        message = 'Expected {}, but got {}'.format(expected, actual)
        assert actual == expected, message 

    def test_windows_phone_platform(self):
        test_agent = 'Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.0; Trident/6.0; IEMobile/10.0; ARM; Touch; NOKIA; Lumia 920)'
        test_platform = 'windows'
        actual = compute_platform_version(test_agent, test_platform)
        expected = 'Windows Phone 8.0'
        message = 'Expected {}, but got {}'.format(expected, actual)
        assert actual == expected, message

    def test_linux_platform(self):
        test_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) snap Chromium/80.0.3987.100 Chrome/80.0.3987.100 Safari/537.36'
        test_platform = 'linux'
        actual = compute_platform_version(test_agent, test_platform)
        expected = 'Linux x86_64'
        message = 'Expected {}, but got {}'.format(expected, actual)
        assert actual == expected, message

    def test_linux_ubuntu_platform(self):
        test_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv: 75.0) Gecko/20100101 Firefox/75.0'
        test_platform = 'linux'
        actual = compute_platform_version(test_agent, test_platform)
        expected = 'Linux x86_64'
        message = 'Expected {}, but got {}'.format(expected, actual)
        assert actual == expected, message

    def test_android_platform(self):
        test_agent = 'Mozilla/5.0 (Linux; Android 5.1.1; Nexus 5 Build/LMY48B; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/43.0.2357.65 Mobile Safari/537.36'
        test_platform = 'android'
        actual = compute_platform_version(test_agent, test_platform)
        expected = 'Android 5.1.1'
        message = 'Expected {}, but got {}'.format(expected, actual)
        assert actual == expected, message

    def test_macintosh_platform(self):
        test_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv: 75.0) Gecko/20100101 Firefox/75.0'
        test_platform = 'macos'
        actual = compute_platform_version(test_agent, test_platform)
        expected = 'Mac OS X 10.13'
        message = 'Expected {}, but got {}'.format(expected, actual)
        assert actual == expected, message

    def test_macintosh_plain_platform(self):
        test_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36'
        test_platform = 'macos'
        actual = compute_platform_version(test_agent, test_platform)
        expected = 'Mac OS X 10_10_2'
        message = 'Expected {}, but got {}'.format(expected, actual)
        assert actual == expected, message

    def test_iphone_platform(self):
        test_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1'
        test_platform = 'iphone'
        actual = compute_platform_version(test_agent, test_platform)
        expected = 'iPhone OS 10_3_1'
        message = 'Expected {}, but got {}'.format(expected, actual)
        assert actual == expected, message

    def test_ipad_platform(self):
        test_agent = 'Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405'
        test_platform = 'ipad'
        actual = compute_platform_version(test_agent, test_platform)
        expected = 'OS 3_2_1'
        message = 'Expected {}, but got {}'.format(expected, actual)
        assert actual == expected, message

    def test_ipad_plain_platform(self):
        test_agent = 'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
        test_platform = 'ipad'
        actual = compute_platform_version(test_agent, test_platform)
        expected = 'OS 6_0'
        message = 'Expected {}, but got {}'.format(expected, actual)
        assert actual == expected, message

    def test_no_platform_values(self):
        test_agent = 'PostmanRuntime/7.24.0'
        test_platform = ''
        actual = compute_platform_version(test_agent, test_platform)
        expected = None
        message = 'Expected {}, but got {}'.format(expected, actual)
        assert actual == expected, message

