from multiThreadRender import MultiThreadRender
from multiThreadRender import UpdateRenderWidget
from nukescripts import panels


def add_render_knob():
    node = nuke.thisNode()
    root_node = nuke.root()
    try:
        node['RenderThread'].value()
        render_knob = "exist"
    except:
        render_knob = "not exist"

    if render_knob == "not exist":
        render_tab = nuke.Tab_Knob("RenderThread", "RenderThread")
        range_first_knob = nuke.Int_Knob("custom_first", "Frame Range")
        range_last_knob = nuke.Int_Knob("custom_last", "")
        range_last_knob.clearFlag(nuke.STARTLINE)
        divider_line = nuke.Text_Knob("divider", "")
        thread_knob = nuke.PyScript_Knob("SubmitRender")
        thread_knob.setFlag(nuke.STARTLINE)

        range_first_knob.setValue(int(root_node['first_frame'].value()))
        range_last_knob.setValue(int(root_node['last_frame'].value()))
        thread_knob.setValue("""
try:
    nuke.scriptSave()
    UpdateRenderWidget(render_panel, nuke.thisNode())
except Exception as error:
    print(error)
        """)
        node.addKnob(render_tab)
        node.addKnob(range_first_knob)
        node.addKnob(range_last_knob)
        node.addKnob(divider_line)
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

