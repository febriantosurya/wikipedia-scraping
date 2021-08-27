from data_manager.school import School


class DataManager:
  def __init__(self):
    self.local_data_path = './data.tsv'
    self.schools_from_google_sheet = {}
    self.schools_from_local_data = {}

    self.__get_schools_from_local_data()

  
  def __get_schools_from_local_data(self):
    try:
      with open(self.local_data_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
          line = line.replace('\n', '')
          school = School.from_string(line)
          self.schools_from_local_data[int(school.index)] = school
    except Exception as e:
      pass


  def write_schools_into_local_data(self):
    with open(self.local_data_path, 'w') as file:
      for _, school in self.schools_from_local_data.items():
        school_str = school.to_string()
        file.write(school_str + '\n')


  def sync_schools(self):
    for _, school_from_local_data in self.schools_from_local_data.items():
      school_from_google_sheet = self.schools_from_google_sheet.get(school_from_local_data.index, None)
      if school_from_google_sheet is not None:
        school_from_google_sheet.index                = school_from_local_data.index
        school_from_google_sheet.code                 = school_from_local_data.code
        school_from_google_sheet.state                = school_from_local_data.state
        school_from_google_sheet.name                 = school_from_local_data.name
        school_from_google_sheet.priority             = school_from_local_data.priority
        school_from_google_sheet.color                = school_from_local_data.color
        school_from_google_sheet.last_scraped_status  = school_from_local_data.last_scraped_status
        school_from_google_sheet.last_scraped_message = school_from_local_data.last_scraped_message

    for _, school_from_google_sheet in self.schools_from_google_sheet.items():
      school_from_local_data = self.schools_from_local_data.get(school_from_google_sheet.index, None)
      if school_from_local_data is None:
        school = School.from_school(school_from_google_sheet)
        self.schools_from_local_data[school.index] = school
