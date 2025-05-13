from .base_component import BaseComponent
import matplotlib.pyplot
from fasthtml.common import Img
import matplotlib.pylab as plt
import matplotlib
import io
import base64

# Prevent memory leaks from matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['savefig.transparent'] = True
matplotlib.rcParams['savefig.format'] = 'png'


def matplotlib2fasthtml(func):
    '''
    Converts a matplotlib plot to a FastHTML-compatible image component using base64-encoded PNG.
    '''
    def wrapper(*args, **kwargs):
        fig = plt.figure()

        # Run the user's visualization logic
        func(*args, **kwargs)

        # Save the figure to a base64-encoded PNG
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, transparent=True)
        img_buffer.seek(0)
        base64_data = base64.b64encode(img_buffer.read()).decode()

        # Close the figure to prevent memory leaks
        plt.close(fig)
        plt.close('all')

        return Img(src=f'data:image/png;base64,{base64_data}')
    return wrapper


class MatplotlibViz(BaseComponent):
    '''
    Base class for creating matplotlib visualizations as FastHTML image components.
    Override the `visualization` method in subclasses.
    '''

    @matplotlib2fasthtml
    def build_component(self, entity_id, model):
        return self.visualization(entity_id, model)

    def visualization(self, entity_id, model):
        '''
        Override this method to define a matplotlib plot.
        '''
        pass

    def set_axis_styling(self, ax, bordercolor='white', fontcolor='white'):
        ax.title.set_color(fontcolor)
        ax.xaxis.label.set_color(fontcolor)
        ax.yaxis.label.set_color(fontcolor)

        ax.tick_params(color=bordercolor, labelcolor=fontcolor)

        for spine in ax.spines.values():
            spine.set_edgecolor(bordercolor)

        for line in ax.get_lines():
            line.set_linewidth(4)
            line.set_linestyle('dashdot')
