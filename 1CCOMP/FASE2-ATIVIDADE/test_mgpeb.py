import mgpeb as m

def codigos(registros):
    return [r['codigo'] for r in registros]

modulos = m.criar_modulos_equipe()
assert len(modulos) == 10
assert m.buscar_menor_combustivel(modulos)['codigo'] == 'MD10'
assert m.buscar_maior_prioridade(modulos)['codigo'] == 'MD03'
assert codigos(m.buscar_por_carga(modulos, 'medicina')) == ['MD03']
assert m.buscar_por_carga(modulos, 'Inexistente') == []
assert m.buscar_por_codigo(modulos, 'XX') is None
assert m.buscar_menor_combustivel([]) is None
assert m.buscar_maior_prioridade([]) is None
assert not m.cadastrar_modulo(modulos, 'MD01', 'X', 'X', 1, 70, 1, 'Alta')
assert not m.cadastrar_modulo(modulos, 'XX', 'X', 'X', 0, 70, 1, 'Alta')
assert not m.cadastrar_modulo(modulos, 'XX', 'X', 'X', 1, 101, 1, 'Alta')
assert not m.cadastrar_modulo(modulos, 'XX', 'X', 'X', 1, 70, 0, 'Alta')
fila = modulos[:]
m.ordenar_fila(fila)
assert codigos(fila) == ['MD03','MD02','MD01','MD05','MD04','MD09','MD08','MD06','MD10','MD07']
assert codigos(modulos) == ['MD01','MD02','MD03','MD04','MD05','MD06','MD07','MD08','MD09','MD10']
a, b = modulos[0].copy(), modulos[0].copy()
b['codigo'] = 'EMPATE'
f = [a,b]; m.ordenar_fila(f)
assert codigos(f) == ['MD01','EMPATE']
m.ordenar_fila([])
assert m.decidir_pouso(modulos[0], True, True) == 'AUTORIZADO'
assert m.decidir_pouso(modulos[2], True, True) == 'ALERTA'
assert m.decidir_pouso(modulos[0], False, True) == 'ESPERA'
assert m.decidir_pouso(modulos[0], True, False) == 'ESPERA'
r = modulos[0].copy(); r['massa'] = 12001
assert m.decidir_pouso(r, True, True) == 'ESPERA'
r['massa'] = 12000; r['combustivel'] = 50
assert m.decidir_pouso(r, True, True) == 'AUTORIZADO'
r['combustivel'] = 49
assert m.decidir_pouso(r, True, True) == 'ALERTA'
r['combustivel'] = 50; r['impedimento'] = True
assert m.decidir_pouso(r, True, True) == 'ALERTA'
p, e, alertas = [], [], []
m.processar_rodada(fila,p,e,alertas,True,True,False)
assert len(fila) == 0 and len(p) == 8 and len(e) == 0
assert codigos(alertas) == ['MD03','MD10']
assert m.retirar_alerta(alertas)['codigo'] == 'MD10'
assert m.retirar_alerta(alertas)['codigo'] == 'MD03'
assert m.retirar_alerta(alertas) is None
f, p, e, alertas = [modulos[0]], [], [], []
m.processar_rodada(f,p,e,alertas,False,True,False)
assert codigos(e) == ['MD01'] and not p
m.recolocar_espera(f,e)
assert not e and codigos(f) == ['MD01']
m.processar_rodada(f,p,e,alertas,True,True,False)
assert codigos(p) == ['MD01'] and not f and not e
print('Todos os testes passaram: buscas, cadastro, ordenação, limites, decisões, FIFO/LIFO e reavaliação.')
