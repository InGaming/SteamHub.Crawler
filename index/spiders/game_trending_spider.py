import scrapy
import json
import re
import datetime
from scrapy.http.request import Request
from orator import DatabaseManager


class GameTrending(scrapy.Spider):
    name = "game_trending"
    start_urls = [
        'https://store.steampowered.com/stats/',
    ]

    def parse(self, response):
        db_config = self.settings.get('DB')
        config = {
            'mysql': {
                'driver': db_config['driver'],
                'host': db_config['host'],
                'port': db_config['port'],
                'database': db_config['database'],
                'user': db_config['user'],
                'password': db_config['password'],
                'prefix': db_config['prefix']
            }
        }

        db = DatabaseManager(config)
        datetime_utc_plus8 = datetime.datetime.utcnow() + datetime.timedelta(hours=+8)
        datetime_parse = datetime_utc_plus8.strftime('%Y-%m-%d %H:%M:%S')
        for element in response.css('.player_count_row'):
          now = element.css('td:nth-child(1) > span::text').extract_first()
          total = element.css('td:nth-child(2) > span::text').extract_first()
          title = element.css('td:nth-child(4) > a::text').extract_first()
          link = element.css('td:nth-child(4) > a::attr(href)').extract_first()
          appid = re.search('-?[1-9]\d*',link).group(0)
          select_data = db.table('Trending').where({
              'AppID': appid,
              'Title': title
          }).order_by('Created', 'desc').first()

          if select_data:
            if now == select_data['Now'] and total == select_data['Total']:
              pass
            else:
              db.table('Trending').insert({
                  'AppID': appid,
                  'Title': title,
                  'Total': str(total),
                  'Now': str(now),
                  'Created': datetime_parse
              })
          else:
            db.table('Trending').insert({
                'AppID': appid,
                'Title': title,
                'Total': total,
                'Now': now,
                'Created': datetime_parse
            })