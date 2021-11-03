from tests.logger import Logger

Logger.log('before single_file_import')
import tests.single_file_import.single_file_import
Logger.log('after single_file_import')


if __name__ == '__main__':
  Logger.log('inside if __name__ == __main__')

logs_extractions = Logger.pull_logs()
