"""Layout base dos gráficos Plotly das páginas de análise."""


def apply_custom_layout(fig, *, show_legend: bool = False, hide_x_title: bool = False):
    """
    Limpa o fundo e ajusta o layout base do gráfico Plotly.

    `show_legend` mantém a legenda (gráficos com vários ativos, na Comparação);
    `hide_x_title` remove o título do eixo X quando a data já é evidente.
    """
    xaxis = dict(showgrid=False, zeroline=False)
    if hide_x_title:
        xaxis["title_text"] = ""

    layout = dict(
        title="",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=20, t=20, b=20),
        xaxis=xaxis,
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False),
        font=dict(family="Inter, Arial, sans-serif", color="#334155"),
    )
    if not show_legend:
        layout["showlegend"] = False

    fig.update_layout(**layout)
    return fig
