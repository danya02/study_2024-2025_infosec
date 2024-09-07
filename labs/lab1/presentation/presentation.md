---
## Front matter
lang: ru-RU
title: Лабораторная работа 1
subtitle: Настройка виртуальной машины, Git и Markdown
author:
  - Генералов Даниил, 1032212280
institute:
  - Российский университет дружбы народов, Москва, Россия
date: "2024 год"

## i18n babel
babel-lang: russian
babel-otherlangs: english

## Formatting pdf
toc: false
toc-title: Содержание
slide_level: 2
aspectratio: 169
section-titles: true
theme: metropolis
header-includes:
 - \metroset{progressbar=frametitle,sectionpage=progressbar,numbering=fraction}
---

# Цель работы

Целью данной работы является приобретение практических навыков
установки операционной системы на виртуальную машину, настройки ми-
нимально необходимых для дальнейшей работы сервисов.

– Изучить идеологию и применение средств контроля версий.
– Освоить умения по работе с git.

Научиться оформлять отчёты с помощью легковесного языка разметки Markdown.


# Выполнение

## Виртуальная машина

![virtualbox](../report/image/Screenshot_20240907_150404.png){#fig:001 width=70%}

## Виртуальная машина

![virtualbox error](../report/image/Screenshot_20240907_152701.png){#fig:002 width=70%}

## Виртуальная машина

![virt-manager](../report/image/Screenshot_0001.png){#fig:003 width=70%}

## Виртуальная машина

![rocky linux](../report/image/Screenshot_0002.png){#fig:004 width=70%}

## Виртуальная машина

![rocky linux после настройки](../report/image/Screenshot_0003.png){#fig:005 width=70%}

## Виртуальная машина

![rocky linux после установки](../report/image/Screenshot_0006.png){#fig:010 width=70%}

## Виртуальная машина

![dmesg](../report/image/Screenshot_0007.png){#fig:011 width=70%}

## Git

![git](../report/image/Screenshot_0004.png){#fig:006 width=70%}

## Git

![github](../report/image/Screenshot_20240907_150656.png){#fig:007 width=70%}

## Git

![git clone](../report/image/Screenshot_20240907_151151.png){#fig:008 width=70%}

## Markdown

![markdown-vscode](../report/image/Screenshot_0005.png){#fig:009 width=70%}

# Выводы

В рамках лабораторной работы мы настроили виртуальную машину для выполнения последующих работ --
но не на VirtualBox, а на Qemu/KVM.
Мы также создали репозиторий, в котором мы будем хранить отчеты,
и написали данный отчет и презентацию в Markdown.
