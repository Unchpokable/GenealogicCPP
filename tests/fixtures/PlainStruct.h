#pragma once
#include "Animal.h"

struct PlainStruct : Animal {
    void speak() const override;
};
