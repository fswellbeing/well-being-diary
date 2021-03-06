import logging
import wbd.gui.diary
import wbd.model
import re
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
import wbd.wbd_global

ADD_NEW_HEIGHT_IT = 100
JOURNAL_BUTTON_GROUP_ID_INT = 1
NO_DIARY_ENTRY_EDITING_INT = -1
ADD_DIARY_BN_TEXT_STR = "Add entry"  # -"Add new diary entry"
ADD_AND_NEXT_DIARY_BN_TEXT_STR = "Add and next"
EDIT_DIARY_BN_TEXT_STR = "Edit entry"  # -"Edit diary entry"
EDIT_AND_NEXT_DIARY_BN_TEXT_STR = "Edit and next"

# TODO: Pressing esc will cancel adding or editing diary entry


class CompositeCentralWidget(QtWidgets.QWidget):

    journal_button_toggled_signal = QtCore.pyqtSignal()
    text_added_to_diary_signal = QtCore.pyqtSignal()
    # set_calendar_to_date_signal = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.updating_gui_bool = False

        self.editing_diary_entry_int = NO_DIARY_ENTRY_EDITING_INT


        hbox_l1 = QtWidgets.QHBoxLayout()
        self.setLayout(hbox_l1)

        self.details = wbd.gui.details.CompositeDetailsWidget()
        hbox_l1.addWidget(self.details)

        self.vbox_l2 = QtWidgets.QVBoxLayout()
        hbox_l1.addLayout(self.vbox_l2)

        hbox_l3 = QtWidgets.QHBoxLayout()
        self.vbox_l2.addLayout(hbox_l3)

        hbox_l3.addStretch(1)
        self.prev_page_qpb = QtWidgets.QPushButton("<")
        self.prev_page_qpb.setFixedWidth(30)
        self.prev_page_qpb.clicked.connect(self.on_prev_page_button_clicked)
        hbox_l3.addWidget(self.prev_page_qpb)
        self.page_number_qll = QtWidgets.QLabel()
        hbox_l3.addWidget(self.page_number_qll)
        self.next_page_qpb = QtWidgets.QPushButton(">")
        self.next_page_qpb.setFixedWidth(30)
        self.next_page_qpb.clicked.connect(self.on_next_page_button_clicked)
        hbox_l3.addWidget(self.next_page_qpb)

        # **Adding the diary list**
        self.diary_widget = wbd.gui.diary.DiaryListCompositeWidget()
        ##diary_widget.add_text_to_diary_button_pressed_signal.connect(self.on_diary_add_entry_button_pressed)
        self.diary_widget.context_menu_change_date_signal.connect(self.on_diary_context_menu_change_date)
        self.diary_widget.context_menu_delete_signal.connect(self.on_diary_context_menu_delete)
        self.diary_widget.diary_entry_left_clicked_signal.connect(self.on_diary_entry_left_clicked)
        self.vbox_l2.addWidget(self.diary_widget)

        # Adding new diary entry..
        adding_area_hbox_l3 = QtWidgets.QHBoxLayout()

        self.time_of_day_qsr = QtWidgets.QSlider()
        self.time_of_day_qsr.setOrientation(QtCore.Qt.Vertical)
        self.time_of_day_qsr.setMinimum(0)
        self.time_of_day_qsr.setMaximum(23)
        self.time_of_day_qsr.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.time_of_day_qsr.setTickInterval(6)
        self.time_of_day_qsr.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        self.time_of_day_qsr.valueChanged.connect(self.hour_slider_changed)
        adding_area_hbox_l3.addWidget(self.time_of_day_qsr)

        datetime_vbox_l4 = QtWidgets.QVBoxLayout()
        adding_area_hbox_l3.addLayout(datetime_vbox_l4)

        self.date_qde = QtWidgets.QDateEdit()
        datetime_vbox_l4.addWidget(self.date_qde)

        self.time_of_day_qte = QtWidgets.QTimeEdit()
        # self.time_of_day_qte.setDisplayFormat("HH:MM")
        datetime_vbox_l4.addWidget(self.time_of_day_qte)

        minute_grid_l5 = QtWidgets.QGridLayout()
        datetime_vbox_l4.addLayout(minute_grid_l5)
        MINUTE_BUTTON_WIDTH_INT = 32
        self.minute_0_qpb = QtWidgets.QPushButton("00")
        qfont = self.minute_0_qpb.font()
        qfont.setPointSize(8)
        self.minute_0_qpb.setFont(qfont)
        self.minute_0_qpb.setFixedWidth(MINUTE_BUTTON_WIDTH_INT)
        minute_grid_l5.addWidget(self.minute_0_qpb, 0, 0)
        # datetime_vbox_l4.addWidget(self.minute_0_qpb)
        self.minute_15_qpb = QtWidgets.QPushButton("15")
        self.minute_15_qpb.setFont(qfont)
        self.minute_15_qpb.setFixedWidth(MINUTE_BUTTON_WIDTH_INT)
        minute_grid_l5.addWidget(self.minute_15_qpb, 0, 1)
        # datetime_vbox_l4.addWidget(self.minute_15_qpb)
        self.minute_30_qpb = QtWidgets.QPushButton("30")
        self.minute_30_qpb.setFont(qfont)
        self.minute_30_qpb.setFixedWidth(MINUTE_BUTTON_WIDTH_INT)
        minute_grid_l5.addWidget(self.minute_30_qpb, 1, 0)
        # datetime_vbox_l4.addWidget(self.minute_30_qpb)
        self.minute_45_qpb = QtWidgets.QPushButton("45")
        self.minute_45_qpb.setFont(qfont)
        self.minute_45_qpb.setFixedWidth(MINUTE_BUTTON_WIDTH_INT)
        minute_grid_l5.addWidget(self.minute_45_qpb, 1, 1)
        # datetime_vbox_l4.addWidget(self.minute_45_qpb)


        # ..text input area
        self.adding_text_to_diary_textedit_w6 = CustomQTextEdit(self)
        new_font = QtGui.QFont()
        new_font.setPointSize(12)
        self.adding_text_to_diary_textedit_w6.setFont(new_font)
        self.adding_text_to_diary_textedit_w6.setStyleSheet("background-color:#d0e8c9")
        ###self.adding_text_to_diary_textedit_w6.setText("<i>New diary entry</i>")
        self.adding_text_to_diary_textedit_w6.setFixedHeight(ADD_NEW_HEIGHT_IT)
        adding_area_hbox_l3.addWidget(self.adding_text_to_diary_textedit_w6)
        # .."add new buttons"
        edit_diary_entry_vbox_l4 = QtWidgets.QVBoxLayout()
        ###diary_entry_label = QtWidgets.QLabel("<h4>New diary entry </h4>")
        ###edit_diary_entry_vbox_l4.addWidget(diary_entry_label)

        self.journals_qcb = QtWidgets.QComboBox()
        self.journals_qcb.setMaximumWidth(100)
        for journal in wbd.model.JournalM.get_all():
            self.journals_qcb.addItem(journal.title_str)
        self.journals_qcb.activated.connect(self.journals_activated)
        edit_diary_entry_vbox_l4.addWidget(self.journals_qcb)

        self.rating_qbuttongroup = QtWidgets.QButtonGroup(self)
        self.rating_qbuttongroup.buttonToggled.connect(self.on_rating_toggled)

        hbox_l5 = QtWidgets.QHBoxLayout()
        edit_diary_entry_vbox_l4.addLayout(hbox_l5)

        self.rating_one_qrb = QtWidgets.QRadioButton("1")
        self.rating_qbuttongroup.addButton(self.rating_one_qrb, 1)
        hbox_l5.addWidget(self.rating_one_qrb)

        self.rating_two_qrb = QtWidgets.QRadioButton("2")
        self.rating_qbuttongroup.addButton(self.rating_two_qrb, 2)
        hbox_l5.addWidget(self.rating_two_qrb)

        self.rating_three_qrb = QtWidgets.QRadioButton("3")
        self.rating_qbuttongroup.addButton(self.rating_three_qrb, 3)
        hbox_l5.addWidget(self.rating_three_qrb)

        self.rating_one_qrb.setChecked(True)

        self.add_bn_w3 = QtWidgets.QPushButton(ADD_DIARY_BN_TEXT_STR)
        self.add_bn_w3.setFixedHeight(40)
        edit_diary_entry_vbox_l4.addWidget(self.add_bn_w3)
        # noinspection PyUnresolvedReferences
        self.add_bn_w3.clicked.connect(self.on_add_text_to_diary_button_clicked)
        self.add_and_next_qbn_w3 = QtWidgets.QPushButton(ADD_AND_NEXT_DIARY_BN_TEXT_STR)
        edit_diary_entry_vbox_l4.addWidget(self.add_and_next_qbn_w3)
        self.add_and_next_qbn_w3.hide()  # -TODO: add this again?
        self.cancel_editing_qbn_w3 = QtWidgets.QPushButton("Cancel editing")
        self.cancel_editing_qbn_w3.clicked.connect(self.on_cancel_clicked)
        self.cancel_editing_qbn_w3.hide()
        edit_diary_entry_vbox_l4.addWidget(self.cancel_editing_qbn_w3)
        adding_area_hbox_l3.addLayout(edit_diary_entry_vbox_l4)

        self.vbox_l2.addLayout(adding_area_hbox_l3)

        self.update_gui()

    """
    def update_gui_journal_buttons(self):
        journalm_list = bwb_model.JournalM.get_all()
    """

    def on_rating_toggled(self):
        pass

    def journals_activated(self, i_index: int):
        journal_text_str = self.journals_qcb.itemText(i_index)

        journal_text_edited_str = wbd.wbd_global.format_to_hashtag(journal_text_str)

        logging.debug("journal_text = " + journal_text_edited_str)
        prev_text_cursor = self.adding_text_to_diary_textedit_w6.textCursor()
        self.adding_text_to_diary_textedit_w6.moveCursor(QtGui.QTextCursor.End)
        self.adding_text_to_diary_textedit_w6.insertPlainText(journal_text_edited_str)
        self.adding_text_to_diary_textedit_w6.setTextCursor(prev_text_cursor)

        # Please note: There can be advantages of having the hashtags/journals on a new line, but if we want to
        # have it on the same line as the user is on (without a new line) this can help us:
        # https://stackoverflow.com/a/18134824/2525237

    def hour_slider_changed(self, i_value: int):
        qtime = QtCore.QTime(i_value, 0)
        self.time_of_day_qte.setTime(qtime)

    def on_cancel_clicked(self):
        self.adding_text_to_diary_textedit_w6.clear()
        self.editing_diary_entry_int = NO_DIARY_ENTRY_EDITING_INT
        self.update_gui()

    def on_diary_entry_left_clicked(self, i_diary_entry_id: int):
        if self.adding_text_to_diary_textedit_w6.toPlainText().strip():
            return  # -we don't want to clear away text that has been entered
        if i_diary_entry_id is None:
            return

        self.editing_diary_entry_int = i_diary_entry_id

        diary_entry = wbd.model.DiaryEntryM.get(i_diary_entry_id)
        self.adding_text_to_diary_textedit_w6.setPlainText(diary_entry.diary_text)

        self.update_gui()  # -so that the button texts are updated

    def on_next_page_button_clicked(self):
        wbd.wbd_global.current_page_number_int += 1
        # TODO: Find the max page and check so that we don't exceed this number
        self.update_gui()

    def on_prev_page_button_clicked(self):
        if wbd.wbd_global.current_page_number_int > 0:
            wbd.wbd_global.current_page_number_int -= 1
        self.update_gui()

    def on_journal_button_toggled(self):
        wbd.wbd_global.active_question_id_it = self.journal_qbuttongroup.checkedId()
        self.update_gui()
        self.journal_button_toggled_signal.emit()

    def update_gui(self):
        self.updating_gui_bool = True

        if self.editing_diary_entry_int != NO_DIARY_ENTRY_EDITING_INT:
            diary_entry = wbd.model.DiaryEntryM.get(self.editing_diary_entry_int)
            """
            date_part_int = diary_entry.date_added_it // 86400  # -will be rounded down
            time_part_int = diary_entry.date_added_it % 86400
            """
            qdatetime = QtCore.QDateTime()
            qdatetime.setSecsSinceEpoch(diary_entry.date_added_it)
            self.date_qde.setDate(qdatetime.date())
            self.time_of_day_qte.setTime(qdatetime.time())

        self.page_number_qll.setText(str(wbd.wbd_global.current_page_number_int + 1))

        if self.editing_diary_entry_int != NO_DIARY_ENTRY_EDITING_INT:
            self.add_bn_w3.setText(EDIT_DIARY_BN_TEXT_STR)
            self.add_and_next_qbn_w3.setText(EDIT_AND_NEXT_DIARY_BN_TEXT_STR)
            self.cancel_editing_qbn_w3.show()
        else:
            self.add_bn_w3.setText(ADD_DIARY_BN_TEXT_STR)
            self.add_and_next_qbn_w3.setText(ADD_AND_NEXT_DIARY_BN_TEXT_STR)
            self.cancel_editing_qbn_w3.hide()

        self.diary_widget.update_gui()

        self.updating_gui_bool = False

    def on_diary_context_menu_change_date(self):
        self.update_gui()
        # TODO: Update the calendar as well

    def on_diary_context_menu_delete(self):
        self.update_gui()
        # TODO: Update the calendar as well

    def on_add_text_to_diary_button_clicked(self):
        self.add_text_to_diary()

    def add_text_to_diary(self):
        notes_sg = self.adding_text_to_diary_textedit_w6.toPlainText().strip()

        if self.editing_diary_entry_int != NO_DIARY_ENTRY_EDITING_INT:
            logging.debug("EDITING for self.editing_diary_entry_int = " + str(self.editing_diary_entry_int))
            # -editing a diary entry
            wbd.model.DiaryEntryM.update_note(self.editing_diary_entry_int, notes_sg)

            # TODO: Add the possibility of editing more things here, like the time and date

            # diary_entry = wbd.model.DiaryEntryM.get(self.editing_diary_entry_int)
            #diary_entry.
            qdate = self.date_qde.date()
            qtime = self.time_of_day_qte.time()
            qdatetime = QtCore.QDateTime(qdate, qtime)
            # qdatetime.setDate(qdate)
            # qdatetime.setTime(qtime)
            total_time_int = qdatetime.toSecsSinceEpoch()
            wbd.model.DiaryEntryM.update_date(self.editing_diary_entry_int, total_time_int)

            self.editing_diary_entry_int = NO_DIARY_ENTRY_EDITING_INT

        else:
            # -adding a new diary entry
            if wbd.wbd_global.active_date_qdate == QtCore.QDate.currentDate():
                time_qdatetime = QtCore.QDateTime.currentDateTime()
                unix_time_it = time_qdatetime.toMSecsSinceEpoch() // 1000
            else:
                unix_time_it = wbd.wbd_global.qdate_to_unixtime(wbd.wbd_global.active_date_qdate)
            logging.debug("t_unix_time_it = " + str(unix_time_it))

            selected_rating_int = self.rating_qbuttongroup.checkedId()
            wbd.model.DiaryEntryM.add(
                unix_time_it,
                notes_sg,
                wbd.wbd_global.active_question_id_it,
                selected_rating_int
            )

        self.adding_text_to_diary_textedit_w6.clear()
        # self.update_gui()
        self.text_added_to_diary_signal.emit()


class CustomQTextEdit(QtWidgets.QPlainTextEdit):
    # -for now only plain text input is used. TODO: Maybe we want the change this in the future
    ref_central = None
    key_press_0_9_for_question_list_signal = QtCore.pyqtSignal(int)
    key_press_up_for_question_list_signal = QtCore.pyqtSignal()
    key_press_down_for_question_list_signal = QtCore.pyqtSignal()

    def __init__(self, i_ref_central):
        super().__init__()
        self.ref_central = i_ref_central

    def keyPressEvent(self, iQKeyEvent):
        if QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            if iQKeyEvent.key() == QtCore.Qt.Key_Enter or iQKeyEvent.key() == QtCore.Qt.Key_Return:
                logging.debug("CtrlModifier + Enter/Return")
                self.ref_central.add_text_to_diary()
                self.key_press_down_for_question_list_signal.emit()
                # -TODO: Change name of signals to focus on goal rather than origin
                return
        elif QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.AltModifier:
            if iQKeyEvent.key() == QtCore.Qt.Key_Down:
                logging.debug("AltModifier + Key_Down")
                self.key_press_down_for_question_list_signal.emit()
                return
            elif iQKeyEvent.key() == QtCore.Qt.Key_Up:
                logging.debug("AltModifier + Key_Up")
                self.key_press_up_for_question_list_signal.emit()
                return
            elif iQKeyEvent.key() >= QtCore.Qt.Key_1 or iQKeyEvent.key() >= QtCore.Qt.Key_9:
                logging.debug("AltModifier + Key_0-9")
                new_row_int = 0
                if iQKeyEvent.key() == QtCore.Qt.Key_1:
                    new_row_int = 0
                elif iQKeyEvent.key() == QtCore.Qt.Key_2:
                    new_row_int = 1
                elif iQKeyEvent.key() == QtCore.Qt.Key_3:
                    new_row_int = 2
                elif iQKeyEvent.key() == QtCore.Qt.Key_4:
                    new_row_int = 3
                elif iQKeyEvent.key() == QtCore.Qt.Key_5:
                    new_row_int = 4
                elif iQKeyEvent.key() == QtCore.Qt.Key_6:
                    new_row_int = 5
                elif iQKeyEvent.key() == QtCore.Qt.Key_7:
                    new_row_int = 6
                elif iQKeyEvent.key() == QtCore.Qt.Key_8:
                    new_row_int = 7
                elif iQKeyEvent.key() == QtCore.Qt.Key_9:
                    new_row_int = 8
                ### self.questions_composite_w3.list_widget.setCurrentRow(new_row_int)
                self.key_press_0_9_for_question_list_signal.emit(new_row_int)
                return
        elif QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
            pass
        else: # -no keyboard modifier
            if iQKeyEvent.key() == QtCore.Qt.Key_Enter or iQKeyEvent.key() == QtCore.Qt.Key_Return:
                # -http://doc.qt.io/qt-5/qguiapplication.html#keyboardModifiers
                # -Please note that the modifiers are placed directly in the QtCore.Qt namespace
                # Alternatively:
                # if QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ShiftModifier:
                # -using bitwise and to find out if the shift key is pressed
                logging.debug("enter or return key pressed in textedit area")
                self.ref_central.add_text_to_diary()
                return

        QtWidgets.QPlainTextEdit.keyPressEvent(self, iQKeyEvent)
        # -if we get here it means that the key has not been captured elsewhere (or possibly
        # (that the key has been captured but that we want "double handling" of the key event)

"""
class CustomPushButton(QtWidgets.QWidget):
    def __init__(self, i_journal_name_str, i_journal_id_int):
        super.__init__(self, i_journal_name_str)
        self.journal_id_it = i_journal_id_int
"""
