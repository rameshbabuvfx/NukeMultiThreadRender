from multiThreadRender import MultiThreadRender
from multiThreadRender import UpdateRenderWidget
import nuke


def add_render_knob():
    node = nuke.thisNode()
    try:
        node['RenderThread'].value()
        render_knob = "exist"
    except:
        render_knob = "not exist"

    if render_knob == "not exist":
        render_tab = nuke.Tab_Knob("RenderThread", "RenderThread")
        knob = nuke.PyScript_Knob("SubmitRender")
        knob.setValue("""
from PySide2.QtWidgets import *

widgets = set()
for obj in QApplication.allWidgets():
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
try:
    nuke.scriptSave()
    UpdateRenderWidget(render_panel, nuke.thisNode())
except Exception as error:
    print(error)
        """)
        node.addKnob(render_tab)
        node.addKnob(knob)


# pane = nuke.getPaneFor("uk.co.thefoundry.MultiThreadRender")
# render_panel = nukescripts.panels.registerWidgetAsPanel(
#     "MultiThreadRender",
#     "Multi Render Thread",
#     "uk.co.thefoundry.MultiThreadRender",
#     True
# ).addToPane(pane)


nuke.addOnCreate(add_render_knob, nodeClass="Write")

