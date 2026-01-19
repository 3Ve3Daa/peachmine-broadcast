"""
🍑 PeachMine » Рассылка
Discord бот для массовой рассылки новостей с красивым UI
"""

import asyncio
import os
import sys
import subprocess

# Создаём event loop ДО импорта discord
if sys.platform == "win32":
    asyncio.set_event_loop(asyncio.new_event_loop())

import discord
from discord.ext import commands
from discord.ui import View, Button
import io
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID")) if os.getenv("GUILD_ID") else None

# Парсим список админов из переменной ADMIN_IDS (через запятую)
admin_ids_str = os.getenv("ADMIN_IDS", os.getenv("ADMIN_ID", ""))
ADMIN_IDS = [int(id.strip()) for id in admin_ids_str.split(",") if id.strip()]

DISCORD_INVITE = os.getenv("DISCORD_INVITE", "https://discord.gg/peachmine")

# Флаг для перезапуска
RESTART_FLAG = False

# ═══════════════════════════════════════════════════════════
# 🎨 СТИЛЬ PEACHMINE
# ═══════════════════════════════════════════════════════════

PEACH_COLOR = 0xFF6B6B      # Основной цвет (персиковый)
SUCCESS_COLOR = 0x2ECC71    # Зелёный (успех)
ERROR_COLOR = 0xE74C3C      # Красный (ошибка)
WARNING_COLOR = 0xF39C12    # Оранжевый (предупреждение)
INFO_COLOR = 0x3498DB       # Синий (информация)

PEACH_EMOJI = "🍑"

# ═══════════════════════════════════════════════════════════
# 🤖 ИНИЦИАЛИЗАЦИЯ БОТА
# ═══════════════════════════════════════════════════════════

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(intents=intents)

# Статистика
last_broadcast = {"success": 0, "failed": 0, "total": 0, "timestamp": None}
start_time = None


# ═══════════════════════════════════════════════════════════
# 🎨 EMBED BUILDER
# ═══════════════════════════════════════════════════════════

def create_embed(title: str, description: str, color: int = PEACH_COLOR, 
                 footer: str = None, thumbnail: bool = False) -> discord.Embed:
    """Создаёт стилизованный Embed в стиле PeachMine"""
    embed = discord.Embed(
        title=f"{PEACH_EMOJI} {title}",
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    embed.set_footer(text=footer or "PeachMine » Рассылка")
    return embed


def create_error_embed(message: str) -> discord.Embed:
    """Embed для ошибок"""
    return create_embed("Ошибка", f"❌ {message}", ERROR_COLOR)


def create_success_embed(message: str) -> discord.Embed:
    """Embed для успеха"""
    return create_embed("Успешно", f"✅ {message}", SUCCESS_COLOR)


# ═══════════════════════════════════════════════════════════
# 🔘 КНОПКИ ПОДТВЕРЖДЕНИЯ
# ═══════════════════════════════════════════════════════════

class ConfirmBroadcastView(View):
    """View с кнопками подтверждения рассылки"""
    
    def __init__(self, message_data: dict, members: list, original_interaction, ref_message):
        super().__init__(timeout=120)
        self.message_data = message_data
        self.members = members
        self.original_interaction = original_interaction
        self.ref_message = ref_message
        self.confirmed = False
    
    @discord.ui.button(label="✅ Отправить рассылку", style=discord.ButtonStyle.success)
    async def confirm_button(self, button: Button, interaction: discord.Interaction):
        if interaction.user.id not in ADMIN_IDS:
            await interaction.response.send_message(
                embed=create_error_embed("Только администратор может подтвердить рассылку"),
                ephemeral=True
            )
            return
        
        self.confirmed = True
        self.disable_all_items()
        
        progress_embed = create_embed(
            "Рассылка",
            f"📤 **Отправка началась...**\n\n"
            f"👥 Получателей: **{len(self.members)}**\n"
            f"⏳ Прогресс: `0/{len(self.members)}`",
            WARNING_COLOR
        )
        await interaction.response.edit_message(embed=progress_embed, view=self)
        await self.do_broadcast(interaction)
    
    @discord.ui.button(label="✏️ Редактировать", style=discord.ButtonStyle.primary)
    async def edit_button(self, button: Button, interaction: discord.Interaction):
        if interaction.user.id not in ADMIN_IDS:
            await interaction.response.send_message(
                embed=create_error_embed("Только администратор может редактировать"),
                ephemeral=True
            )
            return
        
        # Отправляем ссылку на сообщение для редактирования
        edit_embed = create_embed(
            "Редактирование",
            f"✏️ Отредактируйте исходное сообщение и снова используйте `/news`\n\n"
            f"📝 [Перейти к сообщению]({self.ref_message.jump_url})",
            INFO_COLOR
        )
        await interaction.response.edit_message(embed=edit_embed, view=None)
        self.stop()
    
    @discord.ui.button(label="❌ Отменить", style=discord.ButtonStyle.danger)
    async def cancel_button(self, button: Button, interaction: discord.Interaction):
        if interaction.user.id not in ADMIN_IDS:
            await interaction.response.send_message(
                embed=create_error_embed("Только администратор может отменить"),
                ephemeral=True
            )
            return
        
        self.disable_all_items()
        cancel_embed = create_embed(
            "Отменено",
            "🚫 Рассылка была отменена",
            ERROR_COLOR
        )
        await interaction.response.edit_message(embed=cancel_embed, view=self)
        self.stop()
    
    def disable_all_items(self):
        for item in self.children:
            item.disabled = True
    
    async def do_broadcast(self, interaction: discord.Interaction):
        """Выполняет рассылку с обновлением прогресса"""
        global last_broadcast
        
        success = 0
        failed = 0
        total = len(self.members)
        
        content = self.message_data.get("content")
        embeds = self.message_data.get("embeds", [])
        files_data = self.message_data.get("files", [])
        
        print(f"[BROADCAST] Начало: {total} участников")
        
        for i, member in enumerate(self.members):
            try:
                # Создаём файлы для каждого участника
                discord_files = []
                for name, data in files_data:
                    discord_files.append(discord.File(fp=io.BytesIO(data), filename=name))
                
                # Создаём красивый embed для новостей
                news_embed = discord.Embed(
                    title=f"{PEACH_EMOJI} PeachMine | Новости сервера",
                    description=content if content else "",
                    color=PEACH_COLOR,
                    timestamp=datetime.now()
                )
                news_embed.set_footer(text=f"PeachMine » Minecraft Server • {datetime.now().strftime('%d.%m.%Y')}")
                
                # Добавляем инвайт в конце
                invite_text = f"\n\n🔗 **Наш Discord:** {DISCORD_INVITE}"
                
                # Отправляем: если есть оригинальные embeds - их, иначе наш красивый
                if embeds:
                    final_content = (content + invite_text) if content else invite_text
                    await member.send(
                        content=final_content,
                        embeds=embeds,
                        files=discord_files if discord_files else None
                    )
                else:
                    news_embed.description = (content or "") + invite_text
                    await member.send(
                        embed=news_embed,
                        files=discord_files if discord_files else None
                    )
                
                success += 1
                print(f"[OK] {member.name}")
                
            except discord.Forbidden:
                failed += 1
                print(f"[FAIL] Закрыты ЛС: {member.name}")
            except Exception as e:
                failed += 1
                print(f"[ERROR] {member.name}: {e}")
            
            # Обновляем прогресс каждые 5 сообщений
            if (i + 1) % 5 == 0 or i == total - 1:
                progress_embed = create_embed(
                    "Рассылка",
                    f"📤 **Отправка...**\n\n"
                    f"✅ Успешно: **{success}**\n"
                    f"❌ Ошибок: **{failed}**\n"
                    f"⏳ Прогресс: `{i+1}/{total}`",
                    WARNING_COLOR
                )
                try:
                    await interaction.edit_original_response(embed=progress_embed, view=self)
                except:
                    pass
            
            await asyncio.sleep(1.5)
        
        # Сохраняем статистику
        last_broadcast = {
            "success": success,
            "failed": failed,
            "total": total,
            "timestamp": datetime.now()
        }
        
        # Финальный embed
        final_embed = create_embed(
            "Рассылка завершена",
            f"📊 **Результаты:**\n\n"
            f"✅ Успешно отправлено: **{success}**\n"
            f"❌ Не удалось отправить: **{failed}**\n"
            f"👥 Всего участников: **{total}**\n\n"
            f"📈 Успешность: **{round(success/total*100, 1)}%**",
            SUCCESS_COLOR if failed == 0 else WARNING_COLOR
        )
        
        await interaction.edit_original_response(embed=final_embed, view=self)
        print(f"[BROADCAST] Завершено: {success}/{total}")
        
        self.stop()
    
    async def on_timeout(self):
        self.disable_all_items()
        timeout_embed = create_embed(
            "Время истекло",
            "⏰ Время на подтверждение истекло. Рассылка отменена.",
            ERROR_COLOR
        )
        try:
            await self.original_interaction.edit_original_response(embed=timeout_embed, view=self)
        except:
            pass


# ═══════════════════════════════════════════════════════════
# 📨 КОМАНДА /NEWS
# ═══════════════════════════════════════════════════════════

@bot.slash_command(name="news", description="📨 Рассылка сообщения всем участникам", guild_ids=[GUILD_ID])
async def news(ctx: discord.ApplicationContext, message_id: discord.Option(str, "ID сообщения для рассылки", required=True)):
    """Рассылка с подтверждением через кнопки"""
    
    # Проверка админа
    if ctx.author.id not in ADMIN_IDS:
        await ctx.respond(embed=create_error_embed("У вас нет прав для этой команды"), ephemeral=True)
        return
    
    await ctx.defer(ephemeral=True)
    
    # Получаем сообщение по ID
    try:
        ref_message = await ctx.channel.fetch_message(int(message_id))
    except:
        await ctx.followup.send(embed=create_error_embed("Сообщение не найдено. Проверьте ID."), ephemeral=True)
        return
    
    # Получаем участников
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        await ctx.followup.send(embed=create_error_embed("Сервер не найден"), ephemeral=True)
        return
    
    members = [m for m in guild.members if not m.bot]
    
    if not members:
        await ctx.followup.send(embed=create_error_embed("Нет участников для рассылки"), ephemeral=True)
        return
    
    # Подготавливаем данные сообщения
    message_data = {
        "content": ref_message.content,
        "embeds": ref_message.embeds,
        "files": []
    }
    
    for attachment in ref_message.attachments:
        try:
            file_data = await attachment.read()
            message_data["files"].append((attachment.filename, file_data))
        except:
            pass
    
    # Превью сообщения
    preview = ref_message.content[:200] + "..." if len(ref_message.content) > 200 else ref_message.content
    if not preview:
        preview = "*[Embed или изображение]*"
    
    # Embed подтверждения
    confirm_embed = create_embed(
        "Подтверждение рассылки",
        f"📝 **Превью сообщения:**\n```{preview}```\n\n"
        f"👥 **Получателей:** {len(members)}\n"
        f"📎 **Вложений:** {len(message_data['files'])}\n"
        f"📋 **Embed'ов:** {len(message_data['embeds'])}\n\n"
        f"⚠️ Нажмите кнопку для подтверждения",
        WARNING_COLOR
    )
    
    view = ConfirmBroadcastView(message_data, members, ctx, ref_message)
    await ctx.followup.send(embed=confirm_embed, view=view, ephemeral=True)


# ═══════════════════════════════════════════════════════════
# ℹ️ КОМАНДА /INFO
# ═══════════════════════════════════════════════════════════

@bot.slash_command(name="info", description="Информация о боте", guild_ids=[GUILD_ID])
async def info(ctx: discord.ApplicationContext):
    """Отправляет информацию в ЛС админу"""
    
    if ctx.author.id not in ADMIN_IDS:
        await ctx.respond(embed=create_error_embed("У вас нет прав для этой команды"), ephemeral=True)
        return
    
    await ctx.defer(ephemeral=True)
    
    guild = bot.get_guild(GUILD_ID)
    member_count = len([m for m in guild.members if not m.bot]) if guild else 0
    
    # Аптайм
    uptime = "Неизвестно"
    if start_time:
        delta = datetime.now() - start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime = f"{hours}ч {minutes}м {seconds}с"
    
    # Статистика рассылки
    if last_broadcast["timestamp"]:
        broadcast_stats = (
            f"✅ Успешно: **{last_broadcast['success']}**\n"
            f"❌ Ошибок: **{last_broadcast['failed']}**\n"
            f"👥 Всего: **{last_broadcast['total']}**\n"
            f"🕐 {last_broadcast['timestamp'].strftime('%d.%m.%Y %H:%M')}"
        )
    else:
        broadcast_stats = "*Рассылок ещё не было*"
    
    info_embed = create_embed(
        "Информация о боте",
        f"**📊 Статус**\n"
        f"```diff\n+ Онлайн```\n\n"
        f"**⏱️ Аптайм**\n{uptime}\n\n"
        f"**👥 Участников на сервере**\n{member_count}\n\n"
        f"**📨 Последняя рассылка**\n{broadcast_stats}",
        INFO_COLOR
    )
    
    try:
        await ctx.author.send(embed=info_embed)
        await ctx.followup.send(embed=create_success_embed("Информация отправлена в ЛС"), ephemeral=True)
    except:
        await ctx.followup.send(embed=create_error_embed("Не удалось отправить в ЛС"), ephemeral=True)


# ═══════════════════════════════════════════════════════════
# 🔄 КОМАНДА /RESTART (только для локального запуска)
# ═══════════════════════════════════════════════════════════

@bot.slash_command(name="restart", description="🔄 Перезагрузить бота", guild_ids=[GUILD_ID])
async def restart_cmd(ctx: discord.ApplicationContext):
    """Перезагружает бота (работает только локально)"""
    
    if ctx.author.id not in ADMIN_IDS:
        await ctx.respond(embed=create_error_embed("У вас нет прав для этой команды"), ephemeral=True)
        return
    
    restart_embed = create_embed(
        "Перезагрузка",
        "⚠️ Команда перезагрузки работает только при локальном запуске.\n"
        "На Railway используй Redeploy в панели управления.",
        WARNING_COLOR
    )
    await ctx.respond(embed=restart_embed, ephemeral=True)


def get_uptime():
    """Возвращает аптайм в читаемом формате"""
    if not start_time:
        return "Неизвестно"
    delta = datetime.now() - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}ч {minutes}м {seconds}с"


@bot.event
async def on_ready():
    global start_time
    start_time = datetime.now()
    
    # Устанавливаем статус "Играет в mc.peachmine.fun"
    await bot.change_presence(
        activity=discord.Game(name="mc.peachmine.fun"),
        status=discord.Status.online
    )
    
    print(f"{'═'*50}")
    print(f"  {PEACH_EMOJI} PeachMine » Рассылка")
    print(f"{'═'*50}")
    print(f"  Бот: {bot.user}")
    print(f"  Сервер: {GUILD_ID}")
    print(f"  Админы: {ADMIN_IDS}")
    print(f"{'═'*50}\n")
    
    # Отправляем уведомление о запуске админам
    try:
        for admin_id in ADMIN_IDS:
            admin = await bot.fetch_user(admin_id)
            await admin.send(embed=create_embed(
                "Бот запущен",
                f"✅ **PeachMine » Рассылка** успешно запущен!\n\n"
                f"🕐 Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}",
                SUCCESS_COLOR
            ))
    except Exception as e:
        print(f"[WARNING] Не удалось отправить уведомление админам: {e}")


# ═══════════════════════════════════════════════════════════
# 🚀 ЗАПУСК
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"\n{PEACH_EMOJI} Запуск PeachMine » Рассылка...\n")
    
    # Проверка обязательных переменных
    if not TOKEN:
        print("❌ ОШИБКА: TOKEN не найден в переменных окружения!")
        print("Убедись что переменная TOKEN установлена в Railway Variables")
        sys.exit(1)
    
    if not GUILD_ID:
        print("❌ ОШИБКА: GUILD_ID не найден в переменных окружения!")
        print("Убедись что переменная GUILD_ID установлена в Railway Variables")
        sys.exit(1)
    
    if not ADMIN_IDS:
        print("❌ ОШИБКА: ADMIN_IDS не найден в переменных окружения!")
        print("Убедись что переменная ADMIN_IDS установлена в Railway Variables")
        print("Пример: ADMIN_IDS=123456789,987654321")
        sys.exit(1)
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ ОШИБКА при запуске бота: {e}")
        sys.exit(1)
