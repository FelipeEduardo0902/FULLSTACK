from django.shortcuts import render, redirect, get_object_or_404
from .models import Reserva
from .forms import ReservaForm, RetiradaVeiculoForm, DevolucaoVeiculoForm
from veiculos.models import Veiculo
from usuarios.models import Funcionario
from django.contrib import messages
from clientes.models import Cliente

# View para reservar veículo
def reservar_veiculo(request, veiculo_id):
    veiculo = get_object_or_404(Veiculo, id=veiculo_id)

    if request.method == 'POST':
        form = ReservaForm(request.POST, veiculo=veiculo)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.veiculo = veiculo
            reserva.funcionario = Funcionario.objects.first()  # substituir por funcionário logado futuramente
            dias = (reserva.data_fim - reserva.data_inicio).days
            reserva.valor_total = dias * veiculo.preco_locacao
            reserva.save()

            veiculo.status_disponibilidade = False
            veiculo.save()

            return redirect('home')
    else:
        form = ReservaForm(veiculo=veiculo)

    return render(request, 'reservas/reservar.html', {
        'veiculo': veiculo,
        'form': form
    })


# View para listar reservas
def listar_reservas(request):
    q = request.GET.get('q', '')
    sort = request.GET.get('sort', 'data_inicio')
    reservas = Reserva.objects.select_related('cliente', 'veiculo').all()
    if q:
        reservas = reservas.filter(cliente__nome__icontains=q)
    if sort:
        reservas = reservas.order_by(sort)
    from .forms import ReservaForm
    forms = {r.id: ReservaForm(instance=r) for r in reservas}
    return render(request, 'reservas/listar.html', {
        'reservas': reservas,
        'q': q,
        'sort': sort,
        'forms': forms,
    })

# View para registrar retirada
def registrar_retirada(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    veiculo = reserva.veiculo

    if request.method == 'POST':
        form = RetiradaVeiculoForm(request.POST, instance=reserva)
        if form.is_valid():
            retirada = form.save(commit=False)
            retirada.status = "retirada"
            retirada.save()

            veiculo.status_disponibilidade = False
            veiculo.save()

            messages.success(request, "Retirada registrada com sucesso.")
            return redirect('listar_reservas')
    else:
        form = RetiradaVeiculoForm(instance=reserva)

    return render(request, 'reservas/registrar_retirada.html', {
        'reserva': reserva,
        'form': form
    })


# View para registrar devolução
def registrar_devolucao_veiculo(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)

    if request.method == 'POST':
        form = DevolucaoVeiculoForm(request.POST, instance=reserva)
        if form.is_valid():
            devolucao = form.save(commit=False)

            # Validação: combustível final deve ser igual ou superior ao inicial
            nivel_inicial = reserva.nivel_combustivel_inicial
            nivel_final = devolucao.nivel_combustivel_final
            ordem_combustivel = ['muito_baixo', 'baixo', 'meio', 'cheio']

            if ordem_combustivel.index(nivel_final) < ordem_combustivel.index(nivel_inicial):
                form.add_error('nivel_combustivel_final', 'O nível de combustível deve ser igual ou maior do que na retirada.')
            else:
                devolucao.status = 'finalizada'
                devolucao.save()

                reserva.veiculo.status_disponibilidade = True
                reserva.veiculo.save()

                messages.success(request, "Devolução registrada com sucesso.")
                return redirect('listar_reservas')
    else:
        form = DevolucaoVeiculoForm(instance=reserva)

    return render(request, 'reservas/registrar_devolucao_veiculo.html', {
        'reserva': reserva,
        'form': form
    })
    
def historico_reservas_cliente(request):
    clientes = Cliente.objects.all()
    cliente_id = request.GET.get('cliente')  # pega o id do cliente selecionado (por GET)

    reservas = []
    cliente_selecionado = None

    if cliente_id:
        reservas = Reserva.objects.filter(cliente__id=cliente_id).select_related('veiculo')
        cliente_selecionado = Cliente.objects.get(id=cliente_id)

    return render(request, 'reservas/historico_cliente.html', {
        'clientes': clientes,
        'reservas': reservas,
        'cliente_selecionado': cliente_selecionado,
    })

def editar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, "Reserva atualizada com sucesso.")
            return redirect('listar_reservas')
    else:
        form = ReservaForm(instance=reserva)
    return render(request, 'reservas/editar_reserva.html', {'form': form, 'reserva': reserva})

def excluir_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    if request.method == 'POST':
        reserva.delete()
        messages.success(request, "Reserva excluída com sucesso.")
        return redirect('listar_reservas')
    return render(request, 'reservas/excluir_reserva.html', {'reserva': reserva})

