from multiThreadRender import MultiThreadRender
from multiThreadRender import UpdateRenderWidget
from nukescripts import panels


def add_render_knob():
    node = nuke.thisNode()
    try:
        node['RenderThread'].value()
        render_knob = "exist"
    except:
        render_knob = "not exist"

    if render_knob == "not exist":
        render_tab = nuke.Tab_Knob("RenderThread", "RenderThread")
        range_knob = nuke.Enumeration_Knob("FrameRange", "FrameRange", ["Global Range", "Scan Range", "Write Range", "Set Custom"])
        thread_knob = nuke.PyScript_Knob("SubmitRender")
        thread_knob.setFlag(nuke.STARTLINE)
        thread_knob.setValue("""
try:
    nuke.scriptSave()
    UpdateRenderWidget(render_panel, nuke.thisNode())
except Exception as error:
    print(error)
        """)
        node.addKnob(render_tab)
        node.addKnob(range_knob)
        node.addKnob(thread_knob)


class TestPanel(nukescripts.PythonPanel):
    def __init__(self):
        super(TestPanel, self).__init__(title="MultiRenderPanel", id="com.example.WidgetPanel")
        self.customKnob = nuke.PyCustom_Knob("Render Thread Panel", "", "WidgetKnob()")
        self.addKnob(self.customKnob)


class WidgetKnob:
    def makeUI(self):
        self.widget = MultiThreadRender()
        return self.widget


def load_python_panel(python_panel):
    python_panel.addToPane()


pane_menu = nuke.menu("Pane")
render_panel = TestPanel()
pane_menu.addCommand("Multi Thread Render", "load_python_panel(render_panel)")


nuke.addOnCreate(add_render_knob, nodeClass="Write")

