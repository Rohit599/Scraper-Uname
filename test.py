import time
from playwright.sync_api import sync_playwright

# Function to bypass Cloudflare and get the content of the page with a cookie
def bypass_cloudflare_and_get_content_with_cookie(url):
    with sync_playwright() as p:
        # Launch a browser (you can choose between chromium, firefox, and webkit)
        browser = p.chromium.launch(headless=False)  # Set headless=True for headless mode
        context = browser.new_context()

        # Add cookies to the browser context (replace with your actual cookie values)
        context.add_cookies([{
            "name": "cf_clearance",  # Cloudflare clearance cookie name
            "value": "F6oQcxVjBt8S46ZwttWa5Lx.Gjt3umXROXgZ.QCZfA4-1728148182-1.2.1.1-taP1SEGIydmebWuPAOOUqt74W8UuACu1uWCoE3uzCCP3Y45F7WhtrbufPyVrS5BuBud9o1T2BtToAZxgUT2AWNfioabT.z1IT2I5awEIgYTTzZq1LmOqVmm_8Tb9ZHlVP_f.AcMYHw3D12J9ouc6AKeyn5a.ZTYvMT9PbxGAs2Rdr6HkLIjSWBOkfdf5cJCqo7GJxtbEzxxS98eWFPvEtiscC3i.XTXsyl9M13HUm9Dk2jkyWc9i82TyinCHth9lIZuhstRiI5TTi.iZKDOKembC0XiSAD518gpct_8nw5EY9Pt3a6OhZa_KWTynX5EWwbUocs8MruNv1SXwUCtxBMM67aWXRou7wEM6kivFfd6WOQxuWi0TtYZ0QNv_5dtiRn8DbVaXRH65r1EXM39QmI2pfp7GG87wKKEtWBHn1uO290bJcTKFoAPhh0mq9xNc",  # Replace with actual value
            "domain": "ufind.name",  # Domain for which the cookie is valid
            "path": "/",  # Path of the cookie
            "expires": -1,  # -1 means the cookie doesn't expire
            "httpOnly": True,
            "secure": True,
            "sameSite": "Strict"
        }])

        # Open a new page in the browser
        page = context.new_page()

        # Set headers to mimic a real browser (optional)
        page.set_extra_http_headers({
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        })

        # Navigate to the target URL
        page.goto(url)

        # Wait for the page to fully load (you can adjust the sleep time if needed)
        time.sleep(5)

        # Get the content of the page (HTML source)
        page_content = page.content()

        # Close the browser
        browser.close()

        return page_content


# URL that we want to scrape
url = "https://ufind.name/catalog-A-101"

# Get the content of the page with the cookie
content = bypass_cloudflare_and_get_content_with_cookie(url)

# Print or process the content
print(content)
