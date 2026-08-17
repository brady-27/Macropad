// Copyright 2026 Brady
// SPDX-License-Identifier: GPL-2.0-or-later

#include QMK_KEYBOARD_H

enum layer_names {
    _BASE,
};

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    /*
     * ┌──────┬──────┬──────┐
     * │ Prev │ Play │ Next │
     * └──────┴──────┴──────┘
     * Switches on XIAO RP2040 pins 11 / 10 / 9 (GP3 / GP4 / GP2)
     */
    [_BASE] = LAYOUT(
        KC_MPRV, KC_MPLY, KC_MNXT
    )
};
