import string

import dash
import dash_core_components as dcc
import dash_html_components as html

import pytest
from dash.dependencies import Input, Output, State
from dash_express.grouping import make_grouping_by_position
from dash_express import Plugin

# Helpers
from templates.base import BaseTemplate
from util import add_css_class, build_id


def all_component_props(component):
    return [prop for prop in component._prop_names if prop.isidentifier()]


def build_component_with_grouping(component_cls, int_grouping, size):
    component = component_cls()
    props = all_component_props(component)[5 : 5 + size]
    # set component property values
    for i, prop in enumerate(props):
        setattr(component, prop, i)
    # Build prop grouping
    prop_grouping = make_grouping_by_position(int_grouping, props)
    return component, prop_grouping, int_grouping


@pytest.fixture
def scalar_grouping_size(request):
    return 0, 1


@pytest.fixture(params=list(range(0, 5)))
def tuple_grouping_size(request):
    n = request.param
    return tuple(range(n)), n


@pytest.fixture(params=list(range(0, 5)))
def dict_grouping_size(request):
    n = request.param
    return {string.ascii_uppercase[i]: i for i in range(n)}, n


@pytest.fixture(params=list(range(0, 5)))
def mixed_grouping_size(request):
    case = request.param
    if case == 0:
        # tuple of tuples
        grouping = ((0, 1), 2)
        grouping_size = 3
    elif case == 1:
        # Deeply nested tuple of tuples
        grouping = (0, (1, (2, 3), ()), (), (4, ((5, (6, (7, 8))), 9)))
        grouping_size = 10
    elif case == 2:
        # dict of tuples
        grouping = {"A": (0, 1), "B": 2}
        grouping_size = 3
    elif case == 3:
        # dict of dicts
        grouping = dict(
            k0=0,
            k6=dict(k1=1, k2=dict(k3=2, k4=3), k5=()),
            k7=(),
            k13=dict(k8=4, k9=dict(k10=dict(k11=5), k12=6)),
        )
        grouping_size = 7
    else:
        # tuple of mixed
        grouping = (
            dict(
                k0=0,
                k6=dict(k1=1, k2=dict(k3=2, k4=3), k5=()),
                k7=(),
                k13=dict(k8=4, k9=(5, 6), k12=()),
            ),
            7,
            ((8, dict(k13=(9, 10, 11), k14=dict(k15=12))), ()),
        )
        grouping_size = 13

    return grouping, grouping_size


@pytest.fixture(params=[html.Button, dcc.Input])
def component_cls(request):
    return request.param


@pytest.fixture
def component_str_prop(component_cls, scalar_grouping_size):
    int_grouping, size = scalar_grouping_size
    component, prop_grouping, value = build_component_with_grouping(
        component_cls, int_grouping, size
    )
    return component, prop_grouping, value


@pytest.fixture
def component_tuple_prop(component_cls, tuple_grouping_size):
    int_grouping, size = tuple_grouping_size
    component, prop_grouping, value = build_component_with_grouping(
        component_cls, int_grouping, size
    )
    return component, prop_grouping, value


@pytest.fixture
def component_dict_prop(component_cls, dict_grouping_size):
    int_grouping, size = dict_grouping_size
    component, prop_grouping, value = build_component_with_grouping(
        component_cls, int_grouping, size
    )
    return component, prop_grouping, value


@pytest.fixture
def component_mixed_prop(component_cls, mixed_grouping_size):
    int_grouping, size = mixed_grouping_size
    component, prop_grouping, value = build_component_with_grouping(
        component_cls, int_grouping, size
    )
    return component, prop_grouping, value


@pytest.fixture(params=[Input, Output, State])
def dependency(request):
    return request.param


@pytest.fixture
def app():
    return dash.Dash(plugins=[Plugin()])


class TestTemplate(BaseTemplate):
    _valid_roles = ("input", "output", "custom")

    _inline_css = """
        .test-css-class {
            padding: 0px;
         }\n"""

    @classmethod
    def build_labeled_component(cls, component, initial_value, label_id=None):
        # Subclass could use bootstrap or ddk
        if not label_id:
            label_id = build_id("label")
        label = html.Label(id=label_id, children=initial_value)
        container = html.Div(id="container", children=[label, component])
        return container, "children", label, "children"

    @classmethod
    def build_containered_component(cls, component):
        """
        Alternative to bulid_labeled_component for use without label, but for
        Unitform spacing with it
        """
        container = html.Div(id="container", children=component)
        return container, "children"

    @classmethod
    def _add_class_to_component(cls, component):
        if isinstance(component, html.Button):
            add_css_class(component, "test-button-css-class")

    def _perform_layout(self):
        return html.Div(
            id="all-div",
            children=[
                html.Div(id="inputs-div", children=self.get_containers("input")),
                html.Div(id="outputs-div", children=self.get_containers("output")),
                html.Div(id="customs-div", children=self.get_containers("custom")),
            ],
        )

    @classmethod
    def _wrap_layout(cls, layout):
        return html.Div(id="app-div", children=[layout])

    def _configure_app(self, app):
        super()._configure_app(app)
        add_stylesheet = True
        for url in app.config.external_stylesheets:
            if "test_stylesheet" in url:
                add_stylesheet = False
                break

        if add_stylesheet:
            app.config.external_stylesheets.append("http://test_stylesheet.css")


@pytest.fixture
def test_template():
    return TestTemplate()
