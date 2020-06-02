import json
import os


class Downloader():
    def __init__(self,
                 input_url=None,
                 input_json_path=None,
                 input_notion_url=None,
                 target_main_directory=str(os.path.dirname(os.path.abspath(__file__)))+'/'):

        self.target_main_directory = target_main_directory
        self.input_url = input_url
        self.input_json_path = input_json_path
        self.input_notion_url = input_notion_url
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
            # check if a valid notion url
            if not self.input_notion_url.startswith('https://www.notion.so') and not self.input_notion_url.startswith('https://notion.so'):
                print(
                    'Notion URL isnt correctly formated. Make sure to start the URL with "https://www.notion.so"')
                raise SyntaxError

    def download_file(self, url):
        print('Start downloading file: {}'.format(url))
        try:
            os.system(
                'curl "'+url+'" --output '+self.target_main_directory+url.split('/')[-1])
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))

    def download_torrent(self, magnet_link):
        self.setup_torrent()
        print('Start downloading torrent: {}'.format(magnet_link))
        try:
            os.system(
                "/usr/local/bin/webtorrent --out "+self.target_main_directory+" download " + magnet_link)
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

        elif self.input_json_file:
            # for every link from json: change status to "in progress", download file, change status to "downloaded" or "failed"
            for entry in self.input_json_file:
                try:
                    if entry['progress'] != 'in progress' and entry['progress'] != 'done':
                        entry['progress'] = 'in progress'
                        self.save_json()

                        if entry['url'].startswith('magnet:'):
                            self.download_torrent(entry['url'])
                        else:
                            self.download_file(entry['url'])

                        entry['progress'] = 'done'
                        self.save_json()
                except:
                    print(
                        'Failed downloading file. Do you have the permission to download the file and is the url correct?')
                    entry['progress'] = 'failed'
                    self.save_json()

        elif self.input_notion_url:
            # TODO for every link from notion: change status to "in progress", download file, change status to "downloaded" or "failed"
            pass

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
