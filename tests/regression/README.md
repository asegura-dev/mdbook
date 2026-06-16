# Pruebas de regresión

Convención: cuando corrijamos un bug, añadimos aquí un test que falle con el
bug presente y pase con el arreglo. Márcalos con `@pytest.mark.regression` (o
`pytestmark = pytest.mark.regression` a nivel de módulo) y nómbralos según el
síntoma, p. ej. `test_fence_sin_lenguaje_no_rompe.py`.

Aún no hay regresiones registradas.
