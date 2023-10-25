import logging

from aiogram.types import CallbackQuery
from aiogram import Router
from utils.db import connect, close
from keyboards.inline import help_keyboard, question_answer_keyboard, meal_question_keyboard, back_or_main_menu_keyboard, training_question_keyboard, pay_problem_keyboard
router = Router()


@router.callback_query(lambda c: c.data == "help")
async def send_help(callback: CallbackQuery):
    await callback.message.answer(text=f"Добро пожаловать в раздел <b>ПОМОЩИ</b>\n"
                                       f"👉Выберите действие👈", reply_markup=help_keyboard, parse_mode="HTML")
    await callback.answer()


@router.callback_query(lambda c: c.data == "qwestion/answer")
async def send_answer(callback: CallbackQuery):
    await callback.message.answer(text=f"Выберете категорию, по которой у вас появился вопрос:", reply_markup=question_answer_keyboard)
    await callback.answer()

@router.callback_query(lambda c: c.data == "meal_question")
async def send_answer_meal(callback: CallbackQuery):
    await callback.message.answer(text=f"‼️Часто задаваемые вопросы:‼️\n"
                                        f"❓ Включено ли питание? 🍏🍛\n"
                                        f"В моём проекте вы будете получать понедельный план питания.\n"
                                        f"1 раз в неделю, в субботу в 12.00 по московскому времени, вам будет приходить новый рацион, по которому вам необходимо питаться с понедельника по воскресенье.\n"
                                        f"❓ За какое время до и через какое время после тренировки можно есть? 🏋️‍♂️🍌🥤\n"
                                        f"Примём пищи до тренировки плотный за 1,5-2 часа, лёгкий перекус за час, за полчаса можно съесть пару фруктов или выпить свежевыжатый фреш. После тренировки можно сразу есть овощи и белок для восстановления организма, максимум можно добавить крупу.\n"
                                        f"❓ Как и когда правильнее взвешиваться? ⚖️\n"
                                        f"Взвешиваться ли каждый день? 📆\n"
                                        f"Взвешивайтесь утром после пробуждения и туалета голыми и на голодный желудок. Желательно взвешиваться каждый день, чтобы не упустить момента, когда вы начнёте поправляться. Так незаметно можно набрать и 5 кг.\n"
                                        f"❓ Сколько кг реально скинуть за 4 недели проекта? 📉\n"
                                        f"При полном соблюдение рекомендаций: 2-4 кг. Больше и не нужно, так как я против быстрого похудения, организм должен успевать адаптироваться под изменения.\n",
                                        reply_markup=meal_question_keyboard)
    await callback.answer()

    @router.callback_query(lambda c: c.data == "recomendation")
    async def send_recomendation_meal(callback: CallbackQuery):
        await callback.message.answer(text=f"🥦Рекомендации по питанию🥦\n"
                                           f" ❓ Что делать, если очень хочется есть, а все приемы пищи закончились? Или пошёл в ресторан/на др?\n"
                                           f" Если все приемы пищи закончились, то можно поесть овощи и рыбу (без соли и соусов, приготовленные на пару или на гриле)\n"
                                           f" ❓ Надо ли принимать витамины и какие рекомендуете?\n"
                                           f" Рекомендую сдать анализы, чтобы понять чего не хватает вашему организму или пить комплексные витамины.\n"
                                           f" ❓ Сколько яиц можно есть в день?\n"
                                           f" Яйц можно есть неограниченное кол-во, главное желтков в зависимости от вашей массы теле естъ не более 3-6 штук в день.\n"
                                           f" ❓ Если подошло время ужина (4-5 часов до сна), а я не хочу есть. Пропускать?\n"
                                           f" Приемы пищи нельзя пропускать. Питание - это основа и система работы организма.\n"
                                           f" ❓ За какое время до сна надо прекращать пить воду?\n"
                                           f" Пить воду можно в любое время. Вода должна быть очищенная и не газированная.\n"
                                           f" ❓ Как готовить без соли? Еда будет пресна!\n"
                                           f" Мы уже настолько привыкли все солить, что отвыкли от реального вкуса еды. Покупайте свежие качественные продукты и используйте травы и приправы без соли.\n", reply_markup=back_or_main_menu_keyboard)
        await callback.answer()


@router.callback_query(lambda c: c.data == "training_question")
async def send_answer_training(callback: CallbackQuery):
    await callback.message.answer(text=f"‼️Часто задаваемые вопросы:‼️\n"
                                         f"❓ В какое время будут проходить тренировки? ⏰\n"
                                         f"Записи тренировок будут размещаться в понедельник, среду и пятницу в 6 часов утра. Выбор времени обусловлен тем, что в проекте участвует вся Россия, и в некоторых городах разница с Москвой составляет 6, 8 и даже 12 часов!\n"
                                         f"❓ Какое оборудование понадобится для тренировок и можно ли их выполнять в домашних условиях? 🏠🧘‍♀️\n"
                                         f"Тренировки можно выполнять в любом комфортном для вас месте: дома, на улице (спортивная площадка), фитнес клуб. Из оборудования понадобится только коврик, бутылка воды и хорошее настроение!\n"
                                         f"❓ Есть ли ограничения по возрасту? 🧓👧\n"
                                         f"Ограничений по возрасту нет, самому взрослому моему спортсмену 74 года.\n", reply_markup=training_question_keyboard)
    await callback.answer()

    @router.callback_query(lambda c: c.data == "recomendation_training")
    async def send_recomendation_training(callback: CallbackQuery):
        await callback.message.answer(text=f"‼️Часто задаваемые вопросы о тренировках:‼️\n"
                                            f"❓ Какой уровень подготовки должен быть для участия в вашем проекте? Если у меня травмы, могу ли участвовать? 🤕\n"
                                            f"В проекте могут участвовать все! Каждое упражнение будет иметь несколько вариантов выполнения для участников с разным уровнем физической подготовки.\n"
                                            f"❓ Нужно ли повторять предыдущие тренировки в те дни, когда нет новых? Или тренироваться только 3 раза в неделю? 📅🏋️‍♂️\n"
                                            f"Нет, не нужно повторять предыдущие тренировки. Надо тренироваться только три раза в неделю, как у вас указано в расписании.\n"
                                            f"❓ Можно ли тренироваться, если заболел? 🤒💪\n"
                                            f"Тренироваться при болезни можно, но при условии, что нет температуры и нагрузки в таком случае снижаются на 20-30%.\n", reply_markup=back_or_main_menu_keyboard)
        await callback.answer()


@router.callback_query(lambda c: c.data == "problem_pay")
async def send_problem_pay(callback: CallbackQuery):
    await callback.message.answer(text=f"Если у вас появились трудности с оплатой, свяжитесь со специалистом ", reply_markup=pay_problem_keyboard)


@router.callback_query(lambda c: c.data == "training")
async def send_training(callback: CallbackQuery):
    conn = connect()
    cursor = conn.cursor()

    try:
        # Получаем ID пользователя из таблицы users по telegram_user_id
        cursor.execute("SELECT id FROM users WHERE telegram_user_id = %s", (callback.from_user.id,))
        user = cursor.fetchone()
        if not user:
            logging.info(f"Пользователь с telegram_user_id {callback.from_userid} не найден.")
            return

        user_id = user[0]

        # Получаем последнюю отправленную тренировку для пользователя с учетом URL из таблицы training_links
        cursor.execute("""
                SELECT ut.training_number, tl.training_url
                FROM user_trainings ut
                JOIN training_links tl ON ut.training_number = tl.training_number
                WHERE ut.user_id = %s AND ut.is_sent = TRUE
                ORDER BY ut.sent_date DESC
                LIMIT 1
            """, (user_id,))

        last_sent_training = cursor.fetchone()
        if not last_sent_training:
            logging.info(f"Нет отправленных тренировок для пользователя {callback.from_user.id}")
            return

        training_number, training_url = last_sent_training

        # Отправляем пользователю ссылку
        await callback.message.answer(text=f'Ваша последняя тренировка (№{training_number}): {training_url}')

    except Exception as e:
        logging.error(f"Ошибка: {e}")
    finally:
        cursor.close()
        close(conn)