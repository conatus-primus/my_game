# Защита окон от монстров
Учебный проект с использованием pyGame

## Синопсис
Монстры атакуют! Ваша задача - защитить окна дома от налетающих со всех сторон монстров.   
У вас есть один постоянный амулет, который может защитить одно окно. Вы можете менять окно для защиты, перемещая амулет клавишами или мышью. 
Чем больше окон, тем сложнее защититься. Для многооконных домов вам в помощь даются дополнительные амулеты, которые автоматически защищают пару окон. Увы, дополнительные амулеты могут выдержать только фиксированное количество столкновений с монстрами.
Постоянная бдительность!  
Удачи!


## Правила игры
Игроку предлагается выбрать для игры любой дом из коллекции домов.  Каждый дом имеет свою сложность от 1 до 4 в зависимости от количества окон. Для дома определены уровни прохождения игры. На каждом уровне игрок защищает определенное количество окно, на последнем уровне надо защитить все окна дома. Один уровень длится Т секунд.   
Монстры двигаются к окнам. Окно считается защищенным, если в нем находится амулет (вокруг окна подсвечена рамка цветом амулета). При подлете к рамке окна монстр считается пойманным. Пользователь клавишами или мышью передвигает амулет в окно, к которому движется наибольшее количество монстров. Если монстр подлетает к рамке окна, в котором нет амулета, считается, что монстр не был пойман. Для каждого уровня задается процент монстров, которых необходимо поймать. При достижении заданного значения уровень считается пройденным.  
На старших уровнях появляются дополнительные амулеты, которые двигаются автоматически между произвольными окнами и также ловят монстров. На движение дополнительных амулетов игрок не влияет. 


## Создание пользовательской карты    
### Программные ограничения для одной карты
Размер игрового поля 900 х 900 пикселей.  
Максимальное количество окон - 9.  
Идентификаторы окон - path1 … path9.  
Максимальное количество направляющих для одного окна - 9.  
Идентификаторы направляющих для окна с номером N - pathN1 … pathN9.  
Обязательно должен быть хотя бы один уровень с одним вариантом размещения окно и направляющих.  
Максимальное количество уровней - 6.   
Максимальное количество вариантов размещения окон и направляющих в одном уровне - 32.

Максимальный уровень сложности - 6.


## Авторские права на изображения

В программе заимствованы разнообразные картинки из сети Интернет.   
Ссылки на ресурсы картинок игрового поля:    
[100,](https://in.pinterest.com/pin/watercolor-on-instagram-check-out-botanicartsgallery-artist-fnkdesigns-more-ar--326862885464859201/)
[101,](https://www.freepik.com/premium-ai-image/house-with-windows-front-style-minimalist-line-art_137011468.htm)
[102,](https://ru.dreamstime.com/%D1%8D%D1%81%D0%BA%D0%B8%D0%B7-%D0%B8%D0%BB%D0%BB%D1%8E%D1%81%D1%82%D1%80%D0%B0%D1%86%D0%B8%D1%8F-%D1%81%D1%82%D0%B8%D0%BB%D1%8C-%D0%BC%D1%83%D0%BB%D1%8C%D1%82%D1%84%D0%B8%D0%BB%D1%8C%D0%BC%D0%B0-%D0%BA%D0%B8%D1%80%D0%BF%D0%B8%D1%87%D0%BD%D1%8B%D0%B9-%D0%B4%D0%BE%D0%BC-%D1%81-%D0%BE%D0%BA%D0%BD%D0%B0%D0%BC%D0%B8-%D0%B8-image222257705)
[103,](https://ru.pinterest.com/pin/cours-de-peinture-en-ligne-aquarelle-et-acrylique-cours-dart-en-ligne-cours-de-peinture-lhuile--35817759528619885/)
[104,](https://kr.pinterest.com/pin/489555422015766198/)
[105,](https://www.vectorstock.com/royalty-free-vector/winter-vacations-christmas-vector-22622440)
[106,](https://www.istockphoto.com/se/vektor/royal-bl%C3%A5-sagoslott-eller-palace-bygga-vektorillustration-gm850956364-139771155)
[107,](https://ru.freepik.com/premium-vector/cute-cartoon-fairy-princess-castle-house-king-queen-with-blue-roof-isolate-palace_22403166.htm)
[108,](https://ru.pinterest.com/pin/1146869861358423975/)
[109,](https://depositphotos.com/ru/vector/scandinavian-houses-pattern-baby-seamless-print-cartoon-town-nursery-textile-544077014.html)
[110,](https://pixel.one/homework-improvement/255/zelenyy-stilizovannyy-domik-sashi-nikulinoy)
[111,](https://ru.pngtree.com/freepng/thatched-stylized-cartoon-house_14880688.html)  
[853, 857, 941, 969](https://play.google.com/store/apps/details?id=happy.paint.coloring.color.number)
Ссылки на ресурсы картинок мобов:    
[mob2, mob3,](https://astro9811.itch.io/alien-annihilation) 
[mob5](https://pngtree.com/freepng/hello-skeleton-monster_6001945.html)  
[mob6](https://pngtree.com/freepng/ncov-virus-bacteria-monster-villain-cartoon_5333588.html)  
[mob7](https://ru.freepik.com/premium-vector/green-ghost-pixel-art-style_50573505.htm)  
[mob8](https://pngtree.com/freepng/ghost-with-evil-smile-face-in-pixel-art-style_15971173.html)  
[mob9](https://www.vsemayki.ru/product/case_apple_iphone_11_pro_max_matte/3041839)  
Ссылки на ресурсы картинок в технологических целях:    
[окна на заставке,](https://www.vectorstock.com/royalty-free-vector/window-with-glass-and-wooden-frame-vector-36755161)
[окна на заставке(2),](https://gas-kvas.com/risunki-3d/print:page,1,18743-3d-okno-risunok-46-foto.html)
[фон сообщений](https://www.vecteezy.com/free-vector/abstract-beach-background)  
