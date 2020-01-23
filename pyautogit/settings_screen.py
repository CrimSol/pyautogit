"""A subscreen that allows for setting a variety of pyautogit settings.
"""

import os
import datetime
import py_cui.widget_set
import pyautogit
import pyautogit.screen_manager
import pyautogit.logger as LOGGER


class SettingsScreen(pyautogit.screen_manager.ScreenManager):
    """Class representing settings subscreen for pyautogit

    Methods
    -------
    initialize_screen_elements()
        Override of base class, initializes elements, returns widget set
    ask_log_file_path()
        Prompts user to enter log file path
    get_settings_ascii_art()
        Gets an ascii art settings title
    toggle_logging()
        Function that toggles logging for pyautogit
    update_log_file_path()
        Function that updates the target log file path
    refresh_status()
        Override of base class refresh function
    """


    def __init__(self, top_manager):
        """Constructor for SettingsScreen
        """

        super().__init__(top_manager, 'settings screen')


    def initialize_screen_elements(self):
        """Override of base class function. Initializes widgets, and returns widget set
        """

        settings_widget_set = py_cui.widget_set.WidgetSet(12, 6)
        settings_widget_set.add_key_command(py_cui.keys.KEY_BACKSPACE, lambda : self.manager.open_repo_select_window(from_settings=True))
        logo_label = settings_widget_set.add_block_label(self.get_settings_ascii_art(), 0, 0, row_span=2, column_span=3, center=True)
        logo_label.set_standard_color(py_cui.RED_ON_BLACK)
        link_label = settings_widget_set.add_label('Settings Screen - pyautogit v{}'.format(pyautogit.__version__), 0, 3, row_span=2, column_span=3)
        link_label.add_text_color_rule('Settings Screen*', py_cui.CYAN_ON_BLACK, 'startswith', match_type='line')

        debug_log_label = settings_widget_set.add_label('Debug Logging', 2, 0)
        debug_log_label.toggle_border()
        self.debug_log_toggle = settings_widget_set.add_button('Toggle Logs', 2, 1, command=self.toggle_logging)
        self.debug_enter_path_button = settings_widget_set.add_button('Set Log File', 2, 2, command=self.ask_log_file_path)
        self.debug_log_status_label = settings_widget_set.add_label('OFF - {}'.format(LOGGER._LOG_FILE_PATH), 2, 3, column_span=3)
        self.debug_log_status_label.toggle_border()


        editor_label = settings_widget_set.add_label('Default Editor', 3, 0)
        editor_label.toggle_border()
        self.external_editor_toggle = settings_widget_set.add_button('External/Internal', 3, 1, command=self.toggle_editor_type)
        self.external_editor_enter = settings_widget_set.add_button('Select Editor', 3, 2, command=self.ask_default_editor)
        self.editor_status_label = settings_widget_set.add_label('{} - {}'.format(self.manager.editor_type, self.manager.default_editor), 3, 3, column_span=3)
        self.editor_status_label.toggle_border()

        self.settings_info_panel = settings_widget_set.add_text_block('Settings Info Log', 6, 3, row_span=6, column_span=3)
        self.settings_info_panel.is_selectable = False
        self.info_panel = self.settings_info_panel

        self.update_log_file_path('.pyautogit/{}.log'.format(datetime.datetime.today().split(' ')[0]))
        return settings_widget_set


    def add_to_settings_log(self, text):
        """Function that updates the settings info log panel

        Parameters
        ----------
        text : str
            New log item to write to settings info panel
        """

        self.settings_info_panel.set_text('{}\n{}'.format(text, self.settings_info_panel.get()))


    def ask_log_file_path(self):
        """Prompts user to enter log file path
        """

        self.manager.root.show_text_box_popup('Please enter a new log file path', self.update_log_file_path)


    def get_settings_ascii_art(self):
        """Gets ascii art settings logo

        Returns
        -------
        settings_message : str
            Block letter ascii art settings logo
        """

        settings_message = ' ____  ____  ____  ____  __  __ _   ___   ____  \n '
        settings_message = settings_message + '/ ___)(  __)(_  _)(_  _)(  )(  ( \ / __) / ___) \n'
        settings_message = settings_message + '\___ \ ) _)   )(    )(   )( /    /( (_ \ \___ \ \n'
        settings_message = settings_message + '(____/(____) (__)  (__) (__)\_)__) \___/ (____/ '
        return settings_message


    def toggle_editor_type(self):
        """Function that toggles between internal and external editor
        """

        if self.manager.editor_type == 'Internal':
            self.manager.editor_type = 'External'
        else:
            self.manager.editor_type = 'Internal'
        self.add_to_settings_log('Swapped editor type')
        self.refresh_status()


    def toggle_logging(self):
        """Function that enables/disables logging
        """
        
        LOGGER.toggle_logging()
        self.add_to_settings_log('Toggled logging')
        self.refresh_status()


    def ask_default_editor(self):
        """Function that asks user for editor, and then refreshes
        """

        self.manager.root.show_text_box_popup('Please enter a command to open an external text editor', self.update_default_editor)


    def update_default_editor(self, new_editor):
        """Function that updates the new default editor

        Parameters
        ----------
        new_editor : str
            command used to open external editor
        """

        self.manager.default_editor = new_editor
        if self.manager.editor_type == 'Internal':
            self.toggle_editor_type()
        self.add_to_settings_log('Update default editor to: {}'.format(new_editor))
        self.refresh_status()


    def update_log_file_path(self, new_log_file_path):
        """Function that updates log file path if valid

        Parameters
        ----------
        new_log_file_path : str
            Path to new log file
        """

        if os.path.exists(os.path.dirname(new_log_file_path)) and os.access(os.path.dirname(new_log_file_path), os.W_OK):
            LOGGER.set_log_file_path(new_log_file_path)
            self.add_to_settings_log('Update log file path: {}'.format(new_log_file_path))
            self.refresh_status()
        else:
            self.manager.root.show_error_popup('Permission Error', 'The log file path either does not exist, or you do not have write permissions!')


    def refresh_status(self):
        """Override of base class refresh function.
        """

        logging_on_off = 'OFF'
        if LOGGER._LOG_ENABLED:
            logging_on_off = 'ON'
        log_file_path = LOGGER._LOG_FILE_PATH
        self.debug_log_status_label.title = '{} - {}'.format(logging_on_off, log_file_path)

        self.editor_status_label.title = '{} - {}'.format(self.manager.editor_type, self.manager.default_editor)