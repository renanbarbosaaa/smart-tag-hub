# Smart Tag Hub

Um pequeno serviço de backend que redireciona links curtos, criado para tags NFC. Grave um link curto na tag uma única vez e mude o destino sempre que quiser.

Read this in English: [README.md](README.md)

## O que é?

O Smart Tag Hub é um serviço de redirecionamento de links. A tag NFC guarda apenas um link curto. Quando alguém aproxima o celular da tag, o serviço encontra o destino real e leva a pessoa até lá, de forma muito rápida.

## Por que eu criei

Eu vendo cartões NFC que levam as pessoas para lugares como uma página de avaliação do Google, um perfil do Instagram, uma conversa no WhatsApp ou uma landing page.

Eu queria um sistema próprio por três motivos:

- Não quero depender de plataformas de outras pessoas.
- Os chips NFC têm muito pouca memória. Guardar só um link curto deixa o espaço do chip livre.
- Os clientes costumam pedir para trocar o destino depois. Em uma tag comum, isso significa regravar o chip. Com este serviço, eu só mudo o destino no meu sistema e o cartão continua funcionando.

## Como funciona

1. Um link curto é gravado na tag NFC uma única vez.
2. Uma pessoa aproxima o celular da tag.
3. O serviço procura o link curto e envia o celular para o destino atual.
4. Quando o cliente quer um novo destino, só o destino guardado muda. A tag continua exatamente a mesma.

## Funcionalidades

- Criar links curtos para qualquer endereço web válido.
- Redirecionamento rápido para o destino atual.
- Redirecionamentos temporários de propósito, para que os navegadores não guardem destinos antigos.
- Validação dos links curtos e dos endereços de destino.
- Mensagens de erro claras para links desconhecidos ou mal formatados.
- Conjunto de testes automatizados.

## Tecnologias

- Python
- FastAPI
- SQLAlchemy (assíncrono)
- SQLite para desenvolvimento local
- pytest e httpx para testes

## Arquitetura

O projeto segue uma Clean Architecture simplificada, dividida em camadas com responsabilidades claras:

| Camada | Responsabilidade |
| --- | --- |
| `api` | Recebe as requisições web e devolve as respostas. |
| `domain` | Regras de negócio e validações. Não conhece o banco de dados. |
| `infrastructure` | Conversa com o banco de dados e implementa o que o domínio pede. |
| `tests` | Testes automatizados das regras e do fluxo completo. |

Como o domínio não depende do banco de dados, o armazenamento pode mudar no futuro sem reescrever as regras de negócio.

## Como rodar localmente

Você precisa do Python 3.11 ou mais novo.

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
pytest
uvicorn api.main:app --reload
```

## Status do projeto

- Pronto: o núcleo do backend está completo e coberto por testes automatizados.
- Próximo: um banco de dados pronto para produção.
- Próximo: um painel de administração (front end) para ver e gerenciar todos os links em um só lugar.

## Autor

Renan Barbosa - [GitHub](https://github.com/renanbarbosaaa)