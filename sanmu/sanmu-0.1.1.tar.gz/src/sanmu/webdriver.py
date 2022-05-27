import allure
from selenium.webdriver import chrome
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from webdriver_manager.chrome import ChromeDriverManager

all_browser_type = {
    "CHROME": {
        "driver_class": chrome.webdriver.WebDriver,
        "service_class": chrome.service.Service,
        "manager_class": ChromeDriverManager,
        "manager_kwargs": {
            "url": "https://npm.taobao.org/mirrors/chromedriver/",
        },
    },
}


@allure.step("启动浏览器")
def get_webdriver(
    browser_type,
    log_path="webdriver.log",
    **kwargs,
) -> RemoteWebDriver:
    """
    自动就绪webdriver
    运行传递webdriver启动参数，例如：

    driver = get_webdriver("chrome",
                            chrome_options=chrome_options，
                            desired_capabilities=None
                          )
    """
    browser_type = browser_type.upper()
    if browser_type not in all_browser_type:
        raise ValueError(f"不支持的浏览器类型: {browser_type}")
    data = all_browser_type[browser_type]

    driver_class = data["driver_class"]
    service = data["service_class"]
    manager_class = data["manager_class"]
    manager_kwargs = data["manager_kwargs"]

    kwargs["service"] = service(
        executable_path=manager_class(**manager_kwargs).install(),
        log_path=log_path,
    )

    # fix bug
    if browser_type == "CHROME":
        options = chrome.options.Options()
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        kwargs["options"] = options

    return driver_class(**kwargs)
