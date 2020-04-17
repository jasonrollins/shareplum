try:
    from .lodcal_test_settings import TEST_SETTINGS
except ImportError:
    TEST_SETTINGS = {
        "server_url": "https://jrollins.sharepoint.com",
        "version": "2016",
        "site_url": "https://jrollins.sharepoint.com/sites/TestSite",
        "username": "jrollins@jrollins.onmicrosoft.com",
        "test_list": "BlahTestList123",
        "test_folder": "Shared Documents/This Folder"
    }