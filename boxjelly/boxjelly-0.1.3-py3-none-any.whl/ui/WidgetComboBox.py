from PyQt5 import QtWidgets


class WidgetComboBox(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create combo box
        self.combo_box = QtWidgets.QComboBox()
        
        # Create placeholder widget
        self.widget = QtWidgets.QWidget()
        
        # Connect combo box change signal
        self.combo_box.activated.connect(self.on_combo_box_changed)
        
        self.arrange()
    
    def arrange(self):
        """Arrange the widget"""
        # Set vertical layout
        self.setLayout(QtWidgets.QVBoxLayout())
        
        # Set zero margins
        self.layout().setContentsMargins(0, 0, 0, 0)
        
        # Add combo box to layout
        self.layout().addWidget(self.combo_box)
    
    def on_combo_box_changed(self, index):
        """Slot for combo box change signal"""
        # Get the widget
        widget = self.combo_box.itemData(index)
        
        # Set the widget
        self.set_widget(widget)
    
    def set_widget(self, widget):
        """Set the widget"""
        # Hide the current widget
        self.widget.hide()
        
        # Set the widget
        self.widget = widget
        
        # Show the widget
        self.widget.show()
    
    def add_widget(self, widget, name):
        """Add a widget to the combo box"""
        # Add the widget to the combo box
        self.combo_box.addItem(name, widget)
        self.layout().addWidget(widget)
        widget.hide()
    
    def refresh(self):
        """Refresh the loaded widget display status"""
        self.on_combo_box_changed(self.combo_box.currentIndex())