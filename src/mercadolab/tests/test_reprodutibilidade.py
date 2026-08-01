from pytest import CaptureFixture

from mercadolab.scenarios.exemplo_simulacao_anual import main


def test_cenario_anual_eh_reproduzivel_com_mesma_seed(
    capsys: CaptureFixture[str],
) -> None:
    main()
    primeira_saida = capsys.readouterr().out

    main()
    segunda_saida = capsys.readouterr().out

    assert primeira_saida == segunda_saida