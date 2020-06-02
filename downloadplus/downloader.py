import json
import os

from notion.client import NotionClient


class Downloader():
    def __init__(self,
                 input_url=None,
                 input_json_path=None,
                 input_notion_url=None,
                 notion_token=None,
                 target_main_directory=str(os.path.dirname(os.path.abspath(__file__)))+'/'):

        self.target_main_directory = target_main_directory
        self.input_url = input_url
        self.input_json_path = input_json_path
        self.input_notion_url = input_notion_url
        self.notion_token = notion_token
        self.check_for_valid_input()

    def check_for_valid_input(self):
        if self.input_url:
            if type(self.input_url) != str:
                raise TypeError

        elif self.input_json_path:
            with open(self.input_json_path) as json_file:
                self.input_json_file = json.load(json_file)
                for entry in self.input_json_file:
                    # check if 'url' key is in json
                    if 'url' not in entry or not entry['url']:
                        print('"url" key doesnt exist')
                        raise KeyError

        elif self.input_notion_url:
            # check if token is given
            if not self.notion_token:
                print('notion_token is required to access Notion. Look in your cookies in your web browser for "token_v2" when visiting Notion - thats the notion_token')
                raise PermissionError

            # check if a valid notion url
            if not self.input_notion_url.startswith('https://www.notion.so') and not self.input_notion_url.startswith('https://notion.so'):
                print(
                    'input_notion_url isnt correctly formated. Make sure to start the URL with "https://www.notion.so"')
                raise SyntaxError

            # get data and check if they are valid
            self.notion_data = NotionClient(token_v2=self.notion_token).get_block(
                self.input_notion_url).collection.get_rows()

    def download_file(self, url, name=None, target_subfolder=None):
        print('Start downloading file: {}'.format(name if name else url))
        try:
            filetype = url.split('/')[-1].split('.')[-1]
            name = name + \
                ('.' +
                 filetype if filetype else '') if name else url.split('/')[-1]
            target_subfolder = target_subfolder+'/' if target_subfolder else ''

            # create target_subfolder if doesnt exist yet
            if os.path.isdir(self.target_main_directory+target_subfolder) == False:
                os.mkdir(self.target_main_directory+target_subfolder)

            # download file
            os.system(
                'curl "'+url+'" --output '+self.target_main_directory+target_subfolder+name)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

    def download_torrent(self, magnet_link, name=None, target_subfolder=None):
        self.setup_torrent()
        print('Start downloading torrent: {}'.format(
            name if name else magnet_link))
        try:
            target_subfolder = target_subfolder+'/' if target_subfolder else ''

            # create target_subfolder if doesnt exist yet
            if os.path.isdir(self.target_main_directory+target_subfolder) == False:
                os.mkdir(self.target_main_directory+target_subfolder)

            self.target_main_directory = self.target_main_directory+target_subfolder

            os.system(
                "/usr/local/bin/webtorrent --quiet --out "+self.target_main_directory+" download " + magnet_link)
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

    def process(self):
        # if input url, just download it
        if self.input_url:
            # check if url is a magnet link or not
            if self.input_url.startswith('magnet:'):
                self.download_torrent(self.input_url)
            else:
                self.download_file(self.input_url)

        elif self.input_json_path and self.input_json_file:
            # for every link from json: change status to "in progress", download file, change status to "downloaded" or "failed"
            for entry in self.input_json_file:
                try:
                    if entry['progress'] != 'in progress' and entry['progress'] != 'processed':
                        entry['progress'] = 'in progress'
                        self.save_json()

                        if entry['url'].startswith('magnet:'):
                            self.download_torrent(
                                magnet_link=entry['url'],
                                name=entry['name'],
                                target_subfolder=entry['target_subfolder']
                            )
                        else:
                            self.download_file(
                                url=entry['url'],
                                name=entry['name'],
                                target_subfolder=entry['target_subfolder']
                            )

                        entry['progress'] = 'processed'
                        self.save_json()
                except:
                    print(
                        'Failed downloading file. Do you have the permission to download the file and is the url correct?')
                    entry['progress'] = 'failed'
                    self.save_json()

        elif self.input_notion_url:
            # for every link from notion: change status to "in progress", download file, change status to "downloaded" or "failed"
            for entry in self.notion_data:
                try:
                    if entry.progress != 'in progress' and entry.progress != 'processed':
                        entry.progress = 'in progress'

                        if entry.url.startswith('magnet:'):
                            self.download_torrent(
                                magnet_link=entry.url,
                                target_subfolder=entry.target_subfolder
                            )
                        else:
                            self.download_file(
                                url=entry.url,
                                name=entry.name,
                                target_subfolder=entry.target_subfolder
                            )

                        entry.progress = 'processed'
                except:
                    print(
                        'Failed downloading file. Do you have the permission to download the file and is the url correct?')
                    entry.progress = 'failed'

    def setup_torrent(self):
        # make sure npm is installed
        npm = self.which('npm')
        if npm is None:
            print('NodeJS and npm need to be installed first for installing webtorrent - to download torrents. Visit https://nodejs.org/en/')
            exit()

        # make sure webtorrent is installed
        webtorrent = self.which('webtorrent')
        if webtorrent is None:
            print('Installing webtorrent-cli')
            try:
                os.system("sudo npm install webtorrent-cli -g")
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))

    def save_json(self):
        with open(self.input_json_path, 'w') as outfile:
            json.dump(self.input_json_file, outfile, indent=4)

    def which(self, program):
        """
        :param: program: i.e. docker, python etc
        :return: fullpath:  full path for the given binary
        """
        import os

        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

        return None
