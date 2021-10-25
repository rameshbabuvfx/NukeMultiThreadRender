import nukescripts

from multiThreadRender import MultiThreadRender


def add_render_knob():
    node = nuke.thisNode()
    knob = nuke.PyScript_Knob("RenderThread")
    knob.setValue("""
from PySide2 import QtWidgets
widgets = set()
for obj in QtWidgets.QApplication.allWidgets():
    widgets.add(obj.objectName())

id = 'uk.co.thefoundry.MultiThreadRender'

if id not in widgets:
    pane = nuke.getPaneFor("DopeSheet.1")
    render_panel = nukescripts.panels.registerWidgetAsPanel(
        "MultiThreadRender",
        "Multi Render Thread",
        "uk.co.thefoundry.MultiThreadRender",
        True
    ).addToPane(pane)
else:
    pass
    """)
    node.addKnob(knob)


nuke.addOnCreate(add_render_knob, nodeClass="Write")

