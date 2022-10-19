# Game of Life - PyQt project

**Проект для Яндекс.Лицея - "Игра в жизнь", клеточный автомат.**

Место действия игры — размеченная на клетки плоскость, которая может быть безграничной, ограниченной или замкнутой.
Каждая клетка на этой поверхности имеет восемь соседей, окружающих её, и может находиться в двух состояниях: быть «живой» (заполненной) или «мёртвой» (пустой).

Распределение живых клеток в начале игры называется первым поколением, а каждое следующее поколение рассчитывается на основе предыдущего по таким правилам:
- в пустой (мёртвой) клетке, с которой соседствуют три живые клетки, зарождается жизнь;

- если у живой клетки есть две или три живые соседки, то эта клетка продолжает жить; в противном случае (если живых соседей меньше двух или больше трёх) клетка умирает («от одиночества» или «от перенаселённости»).

Игрок не принимает активного участия в игре. Он лишь расставляет или генерирует начальную конфигурацию «живых» клеток, которые затем изменяются согласно правилам. Несмотря на простоту правил, в игре может возникать огромное разнообразие форм. 