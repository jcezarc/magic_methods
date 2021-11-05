class Comida:

    OBJ_RECEITA = lambda ingrediente, receita: receita
    OBJ_INGREDIENTE = lambda ingrediente, receita: ingrediente
    NOME_RECEITA = lambda ingrediente, receita: receita.nome
    NOME_INGREDIENTE = lambda ingrediente, receita: ingrediente.nome
    TOTAL_QUANTIDADES = lambda ingrediente, receita: ingrediente.__quantidade
    EXCLUI_INGREDIENTE = lambda ingrediente, receita: receita.__ingredientes.remove(ingrediente)

    def __init__(self, nome, ingredientes=None):
        self.nome = nome
        self.__ingredientes = []
        self.__quantidade = 1.0
        if ingredientes:
            self.__iadd__(ingredientes)

    def __iadd__(self, outros):
        if not isinstance(outros, list):
            outros = [outros]
        for item in outros:
            if isinstance(item, str):
                encontrado = self.__getitem__(item)
                if encontrado:
                    encontrado.quantidade += 1
                    continue
                item = Comida(item)
            self.__ingredientes.append(item)
        return self

    @property
    def quantidade(self):
        return self.__quantidade

    @quantidade.setter
    def quantidade(self, valor):
        if valor > 0:
            self.__imul__(valor / self.__quantidade)

    def clone(self):
        obj = Comida(self.nome)
        obj.__quantidade = self.__quantidade
        for item in self.__ingredientes:
            obj.__ingredientes.append(item.clone())
        return obj

    def __add__(self, outros):
        return self.clone().__iadd__(outros)

    def __imul__(self, valor):
        self.__quantidade *= valor
        for item in self.__ingredientes:
            item.__imul__(valor)
        return self

    def __mul__(self, valor):
        return self.clone().__imul__(valor)

    def __itruediv__(self, valor):
        return self.__imul__(1/valor)

    def __truediv__(self, valor):
        return self.clone().__imul__(1/valor)

    def __localiza(self, **args):
        busca = args['busca']
        recursiva = args.get('recursiva', False)
        somente_primeira = args.get('somente_primeira', True)
        resultado = []
        for ingrediente in self.__ingredientes:
            if ingrediente.nome == busca:
                resultado.append({
                    'ingrediente': ingrediente,
                    'receita': self
                })
                if somente_primeira:
                    break
            elif recursiva and ingrediente.__ingredientes:
                resultado += ingrediente.__localiza(**args)
        return resultado

    def __contains__(self, busca):
        return self.__localiza(busca=busca, recursiva=True) != []

    def __getitem__(self, busca):
        encontrados = self.__localiza(busca=busca)
        return encontrados[0]['ingrediente'] if encontrados else None

    def todos(self, busca, func):
        '''
        Percorre todos os grupos que contém esse item.
        
        :func - Determina a ação para cada item.
            * OBJ_RECEITA - Retorna cada receita.
            * OBJ_INGREDIENTE - Retorna cada ingrediente.
            * NOME_RECEITA - Retorna o nome de cada receita.
            * NOME_INGREDIENTE - Retorna o nome de cada ingrediente.
            * EXCLUI_INGREDIENTE - Exclui o ingrediente da receita.
            * TOTAL_QUANTIDADES - As quantidades totais de cada ingrediente.

            > Você pode usar sua própria função assim
        '''
        return [func(**item) for item in self.__localiza(
            busca=busca,
            recursiva=True,
            somente_primeira=False
        )]

    def __delitem__(self, nome):
        encontrado = self.__getitem__(nome)
        if encontrado:
            Comida.EXCLUI_INGREDIENTE(encontrado, self)
        return self

    def __dict__(self):
        conteudo = lambda o: o.__dict__() if o.__ingredientes else o.__quantidade
        return {o.nome: conteudo(o) for o in self.__ingredientes}

    def __eq__(self, outro):
        def ordenada(obj):
            return sorted(obj.__ingredientes, key=lambda k: k.nome)
        tamanho = lambda o: len(o.__ingredientes)
        diferencas = [
            lambda o1, o2: o1.nome != o2.nome,
            lambda o1, o2: o1.__quantidade != o2.__quantidade,
            lambda o1, o2: tamanho(o1) != tamanho(o2),
        ]
        if any(func(self, outro) for func in diferencas):
            return False
        for meu, dele in zip(ordenada(self), ordenada(outro)):
            if not meu.__eq__(dele):
                return False
        return True

    def __isub__(self, outro):
        if isinstance(outro, str):
            outro = self.__getitem__(outro)
        if outro:
            if outro.__quantidade > 1:
                outro.quantidade -= 1 # usa a propriedade `quantidade`
            else:
                Comida.EXCLUI_INGREDIENTE(outro, self)
        return self

    def __sub__(self, outro):
        return self.clone().__isub__(outro)

    def __repr__(self, espacos=''):
        return '{}{} {}\n{}'.format(
            espacos, self.__quantidade, self.nome,
            ''.join(
                ingrediente.__repr__(espacos+'\t')
                for ingrediente in self.__ingredientes
            )
        )
