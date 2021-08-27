class School:
  def __init__(self, index, code, state, name, priority):
    self.index = int(index)
    self.code = code
    self.state = state
    self.name = name
    self.priority = priority
    
    self.color = ''
    self.last_scraped_status = ''
    self.last_scraped_message = ''


  def to_string(self):
    school_str = '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}'.format(
      self.index, self.code, self.state, self.name, self.priority,
      self.color, self.last_scraped_status, self.last_scraped_message
    )
    return school_str.replace('\n', '')


  def get_query_string(self):
    return '{0} {1}'.format(self.name, self.state)

    
  @staticmethod
  def from_string(school_string):
    components = school_string.split('\t')
    school = School(
      index=components[0],
      code=components[1],
      state=components[2],
      name=components[3],
      priority=components[4]
    )
    school.color = components[5]
    school.last_scraped_status = components[6]
    school.last_scraped_message = components[7]
    return school


  @staticmethod
  def from_school(_school):
    school = School(
      index=_school.index,
      code=_school.code,
      state=_school.state,
      name=_school.name,
      priority=_school.priority
    )
    school.color = _school.color
    school.last_scraped_status = _school.last_scraped_status
    school.last_scraped_message = _school.last_scraped_message
    return school
