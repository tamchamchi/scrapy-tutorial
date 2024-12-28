import scrapy
from ..items import RoutineItem
from scrapy.loader import ItemLoader

class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["routine.vn"]
    max_page = 10  # Tổng số trang cần duyệt
    max_products = 50  # Số sản phẩm tối đa cần thu thập
    product_count = 0

    def start_requests(self):
        for page in range(1, self.max_page + 1):
            url = f"https://routine.vn/categories/ao-nam?page={page}"
            yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        # Duyệt qua tất cả các sản phẩm trong trang
        product_links = response.css('a[href*="products"]::attr(href)').getall()
        for link in product_links:
            if self.product_count >= self.max_products:
                self.logger.info("Reached the maximum product limit. Stopping crawler.")
                return
            full_url = response.urljoin(link)
            yield scrapy.Request(full_url, callback=self.parse_item)

    def parse_item(self, response):
        parent_div = response.css('div.sc-7454bded-0.hXtIET.md\\:border-\\[1px\\].z-10.md\\:p-4.md\\:border-border')

        if not parent_div:
            self.logger.warning("Parent div not found!")
            return None

        l = ItemLoader(item=RoutineItem(), selector=parent_div)
        l.add_css("name", 'h1.text-\\[22px\\].font-bold::text')
        l.add_css("price", 'div.text-text-primary.font-semibold.text-\\[16px\\]::text')

        self.product_count += 1
        yield l.load_item()
