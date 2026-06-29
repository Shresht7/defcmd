from defcmd.widgets.select import SelectWidget

def test_select_widget_render():
    w = SelectWidget(prompt="Pick", options=["a", "b"])
    assert "Pick" in w.render()
