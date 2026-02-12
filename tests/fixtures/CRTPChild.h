#pragma once
#include "CRTPBase.h"
#include "Animal.h"

class CRTPChild : public Animal, public CRTPBase<CRTPChild> {
public:
    void speak() const override;
    void implementation();
};
