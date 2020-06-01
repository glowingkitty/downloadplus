import os
import urllib.request


class Downloader():
    def __init__(self,
                 input_url=None,
                 input_text_file=None,
                 input_json_file=None,
                 input_notion_url=None,
                 target_main_directory=os.path.dirname(os.path.abspath(__file__))):

        self.target_main_directory = target_main_directory
        self.input_url = input_url
        self.input_text_file = input_text_file
        self.input_json_file = input_json_file
        self.input_notion_url = input_notion_url
        self.check_for_valid_input()

    def check_for_valid_input(self):
        if self.input_url:
            if type(self.input_url) != str:
                raise TypeError
        elif self.input_text_file:
            # TODO check if text order is correct
            pass
        elif self.input_json_file:
            # TODO check if 'url' and 'targetfolder' keys are in json
            pass
        elif self.input_notion_url:
            # TODO check if a valid notion url
            pass

    def download_file(self, url):
        print('Start downloading file: {}'.format(url))
        urllib.request.urlretrieve(
            url, self.target_main_directory+url.split('/')[-1])

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

        elif self.input_text_file:
            # TODO for every link from textfile: download file, remove link from textfile
            pass

        elif self.input_json_file:
            # TODO for every link from json: change status to "in progress", download file, change status to "downloaded" or "failed"
            pass

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
