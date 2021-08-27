from scraper import ScraperManager
from config import SHEET_ID, SHEET_NAME, SCRAPE_LIMIT
from data_manager.data_manager import DataManager
from data_manager.google_sheet import GoogleSheet


if __name__ == '__main__':
  gs = GoogleSheet(SHEET_ID, SHEET_NAME)
  
  dm = DataManager()
  dm.schools_from_google_sheet = gs.schools
  dm.sync_schools()

  sm = ScraperManager(dm.schools_from_local_data, SCRAPE_LIMIT)
  sm.scrape()

  dm.sync_schools()
  dm.write_schools_into_local_data()

  gs.upload_schools()
