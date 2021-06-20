import sys

from pyke import knowledge_engine
from pyke import krb_traceback

engine = knowledge_engine.engine(__file__)

def main():
    engine.reset()  # allow run tests multiple times

    engine.activate('regras')  # activate engine with 'regras'
    situacao_efluente = ''

    try:
        with engine.prove_goal('regras.vazao($ans)') as gen_vazao:
            for vars5, plan5 in gen_vazao:
                vazaoTanque = vars5['ans']

        with engine.prove_goal(
                'regras.situacao_efluente($res, $ans)') as gen_situacao_efluente:
            for vars, plan in gen_situacao_efluente:
                phEfluente = vars['ans']
                situacao_efluente = vars['res']

                if (vars['res'] == 'efluente_ok'):
                    print('Efluente nao precisa de tratamento!')
                    sys.exit(1)

        with engine.prove_goal('regras.valida_ph_alvo($res, $ans)') as gen_valida_ph_alvo:
            for vars4, plan4 in gen_valida_ph_alvo:
                phalvo = vars4['ans']
                if vars4['res'] == 'pH_invalido':
                    print('pH para correcao invalido!')
                    sys.exit(1)

        engine.add_universal_fact('fatos', 'phAlvo', (phalvo,))  # adiciona o ph alvo nos fatos

        if (situacao_efluente == 'efluente_acido'):
            engine.activate('regras_tratamento')
            print('Tratamento com base')
            try:
                with engine.prove_goal(
                        'regras_tratamento.tratamento_base($res)') as gen_tratamento_base:
                    for vars2, plan2 in gen_tratamento_base:
                        print('Tratamento com base')

                    if (vars2['res'] == 'Hidroxido_de_sodio'):
                        engine.activate('bases')
                        try:
                            with engine.prove_goal(
                                    'bases.componente_sodio($name, $ph)') as gen_componente_sodio:
                                for vars3, plan3 in gen_componente_sodio:
                                    componente = vars3['name']
                                    phComponente = vars3['ph']

                        except Exception:
                            krb_traceback.print_exc()
                            sys.exit(1)

                    if (vars2['res'] == 'Hidroxido_de_calcio'):
                        engine.activate('bases')
                        try:
                            with engine.prove_goal(
                                    'bases.componente_calcio($name, $ph)') as gen_componente_calcio:
                                for vars3, plan3 in gen_componente_calcio:
                                    componente = vars3['name']
                                    phComponente = vars3['ph']

                        except Exception:
                            krb_traceback.print_exc()
                            sys.exit(1)

            except Exception:
                krb_traceback.print_exc()
                sys.exit(1)

        if (situacao_efluente == 'efluente_base'):
            engine.activate('regras_tratamento')
            try:
                with engine.prove_goal(
                        'regras_tratamento.tratamento_acido($res)') as gen_tratamento_acido:
                    for vars2, plan2 in gen_tratamento_acido:
                        print('Tratamento com Acido')

                    if (vars2['res'] == 'Acido_Sulfurico'):
                        engine.activate('acidos')
                        try:
                            with engine.prove_goal(
                                    'acidos.componente_sulf($name, $ph)') as gen_componente_sulf:
                                for vars3, plan3 in gen_componente_sulf:
                                    componente = vars3['name']
                                    phComponente = vars3['ph']
                        except Exception:
                            krb_traceback.print_exc()
                            sys.exit(1)

                    if (vars2['res'] == 'Acido_Nitrico'):
                        engine.activate('acidos')
                        try:
                            with engine.prove_goal(
                                    'acidos.componente_nit($name, $ph)') as gen_componente_nit:
                                for vars3, plan3 in gen_componente_nit:
                                    componente = vars3['name']
                                    phComponente = vars3['ph']

                        except Exception:
                            krb_traceback.print_exc()
                            sys.exit(1)

            except Exception:
                krb_traceback.print_exc()
                sys.exit(1)

    except Exception:
        # This converts stack frames of generated python functions back to the
        # .krb file.
        krb_traceback.print_exc()
        sys.exit(1)



    print('---------- DADOS INFORMADOS ----------')
    print('pH Efluente:', phEfluente)
    print('Vazao tanque:', vazaoTanque, 'm3/h')
    print('pH Alvo:', phalvo)
    print('Componente:', componente)
    print('pH Componente:', phComponente)

    cEfluente = 10 ** -phEfluente
    cComponente = 10 ** -phComponente
    cFinal = 10 ** -phalvo

    engine.add_universal_fact('fatos', 'cComponente', (componente, cComponente))
    engine.add_universal_fact('fatos', 'cEfluente', (phEfluente, cEfluente))

    vazaoComponente = (vazaoTanque * (cEfluente - cFinal))/(cFinal - cComponente)

    print('---------- RESULTADO ----------')
    print('Para regular o pH deste efluente, eh necessario:')
    print(vazaoComponente, "m3/h de", componente)
