---
title: Spare Parts Inventory and Procurement Management
equipment_type: All Equipment
document_type: sop
revision: 1.3
date: 2026-01-30
---

# Spare Parts Inventory and Procurement Management

## 1. Purpose
This procedure establishes the framework for managing spare parts inventory, procurement planning, and stock optimization to minimize downtime and carrying costs.

## 2. Scope
Applies to all spare parts for production equipment including bearings, motors, pumps, belts, seals, electrical components, and consumables.

## 3. Spare Parts Classification

### Critical Spares (Class A)
**Definition**: Parts whose failure causes immediate production stoppage and have long lead times (>7 days)

**Characteristics:**
- High failure impact (complete line shutdown)
- Lead time >1 week
- High replacement cost
- Low interchangeability
- Equipment-specific components

**Examples:**
- Large motor bearings (>6320 size)
- Gearbox assemblies
- Custom pump impellers
- Specialty motor windings
- PLC control modules
- Main drive couplings

**Stocking Policy:**
- Minimum stock: 1 unit per critical equipment
- Maximum stock: 2 units for very critical items
- Review frequency: Monthly
- Reorder point: When stock = 1
- Obsolescence risk: Review annually

### Important Spares (Class B)
**Definition**: Parts for important equipment with moderate lead times (3-7 days)

**Characteristics:**
- Moderate failure impact (partial production loss)
- Lead time 3-7 days
- Moderate cost
- Some interchangeability across equipment
- Standard industrial components

**Examples:**
- Standard bearing sizes (6200-6300 series)
- V-belts and timing belts
- Motor contactors and overload relays
- Mechanical seals for pumps
- Hydraulic hoses and fittings
- Proximity sensors and limit switches

**Stocking Policy:**
- Minimum stock: 1 unit for 2-3 equipment
- Fast-moving items: 2-3 units
- Review frequency: Quarterly
- Reorder point: Based on consumption rate
- Group by equipment type for optimization

### Routine Spares (Class C)
**Definition**: Common consumables and fast-moving items with short lead times (<3 days)

**Characteristics:**
- Low failure impact or redundancy available
- Lead time <3 days
- Low unit cost
- High interchangeability
- Locally available

**Examples:**
- Standard bolts, nuts, washers
- Grease and lubricants
- Cable ties and terminal blocks
- Fuses and pilot lamps
- O-rings and gaskets (standard sizes)
- Cleaning materials

**Stocking Policy:**
- Minimum stock: Based on 30-day consumption
- Bulk purchase for cost savings
- Review frequency: Semi-annually
- Reorder point: When stock = 2 weeks consumption
- Vendor-managed inventory (VMI) where possible

## 4. Inventory Management Principles

### Economic Order Quantity (EOQ)
Calculate optimal order quantity to minimize total cost:

**Formula:**
```
EOQ = √(2 × Annual Demand × Order Cost / Holding Cost per Unit)
```

**Example:**
- Annual bearing usage: 24 units
- Order cost: $100 per order
- Holding cost: $20 per unit per year
- EOQ = √(2 × 24 × 100 / 20) = √240 = 15.5 ≈ 16 units per order

### Reorder Point (ROP)
Set reorder level to avoid stockouts:

**Formula:**
```
ROP = (Average Daily Usage × Lead Time in Days) + Safety Stock
```

**Example:**
- Daily usage: 2 bearings
- Lead time: 7 days
- Safety stock: 5 bearings (for demand variability)
- ROP = (2 × 7) + 5 = 19 bearings

### Safety Stock Calculation
Protect against demand and lead time variability:

**Formula:**
```
Safety Stock = Z-score × √(Average Lead Time × Variance of Demand)
```

Where Z-score:
- 90% service level: 1.28
- 95% service level: 1.65
- 99% service level: 2.33

### ABC Analysis for Inventory Prioritization
- **A-items**: 20% of items, 80% of value → Tight control, frequent review
- **B-items**: 30% of items, 15% of value → Moderate control
- **C-items**: 50% of items, 5% of value → Simple controls, bulk orders

## 5. Spare Parts Sourcing Strategy

### Preferred Supplier Program
Establish relationships with reliable vendors:

**Criteria for Preferred Suppliers:**
- Consistent quality and delivery performance
- Competitive pricing (within 10% of market)
- Emergency delivery capability
- Technical support available
- Minimum 12-month warranty on parts
- Stock availability >90%

**Current Preferred Suppliers:**
- Bearings: SKF, NSK, FAG (local distributors)
- Motors: ABB, Siemens, WEG
- Belts: Gates, Dayco, Continental
- Electrical: Schneider, Allen-Bradley, Phoenix Contact
- Hydraulics: Parker, Bosch Rexroth
- Seals: John Crane, Garlock

### Multi-Sourcing vs Single-Sourcing

**Single-Source (Preferred for Critical Items):**
- Ensures consistency and compatibility
- Leverage volume for better pricing
- Simplifies quality management
- Risk: Supplier dependency

**Multi-Source (For Routine Items):**
- Price competition
- Supply security
- Flexibility in procurement
- Risk: Quality variability

**Recommendation:**
- Critical spares (Class A): Single-source from OEM or approved equivalent
- Important spares (Class B): Primary + backup supplier
- Routine spares (Class C): Multi-source for best price

### OEM vs Aftermarket Parts

**OEM (Original Equipment Manufacturer) Parts:**
- **Advantages**: Guaranteed fit, warranty, reliability
- **Disadvantages**: Higher cost (20-50% premium), longer lead times
- **Use for**: Critical equipment, within warranty period, complex assemblies

**Aftermarket/Generic Parts:**
- **Advantages**: Lower cost, faster availability, competitive market
- **Disadvantages**: Quality variability, shorter life, warranty concerns
- **Use for**: Non-critical equipment, out-of-warranty, standard components

**Quality Assessment for Aftermarket:**
- Verify ISO/industry certifications
- Request material certificates
- Trial period for new suppliers (small quantity first)
- Performance tracking (MTBF comparison)

## 6. Procurement Process

### Emergency Procurement (Unplanned Breakdown)
**Timeline**: <24 hours

**Process:**
1. Identify part number and specifications
2. Check on-site inventory (warehouse + other locations)
3. Contact preferred supplier for immediate delivery
4. If not available:
   - Check sister plants for loan/transfer
   - Search alternative suppliers (OEM + aftermarket)
   - Consider expedited shipping (courier, air freight)
5. Emergency purchase authorization (up to $10K without approval)
6. Receive and inspect parts immediately
7. Update inventory system

**Documentation:**
- Emergency purchase requisition
- Approval email (if >$10K)
- Supplier confirmation
- Delivery tracking number

### Planned Procurement (Routine Replenishment)
**Timeline**: 1-4 weeks

**Process:**
1. System generates purchase requisition when inventory hits ROP
2. Procurement reviews and consolidates orders
3. Request for quotation (RFQ) to preferred suppliers (for >$5K)
4. Evaluate quotes (price, delivery, warranty)
5. Issue purchase order
6. Track delivery (weekly follow-up)
7. Receive, inspect, and stock parts
8. Update inventory system and close PO

**Lead Time by Part Type:**
- Standard bearings/belts: 3-5 days
- Motors (standard frame): 2-4 weeks
- Custom parts: 6-12 weeks
- Imported items: 8-16 weeks

### Blanket Purchase Orders (For High-Volume Items)
**Benefits:**
- Negotiated annual pricing
- Simplified ordering (release against blanket PO)
- Volume discounts (10-20%)
- Reduced administrative workload

**Suitable Items:**
- Consumables (grease, solvents, rags)
- High-usage bearings
- Standard belts and seals
- Electrical consumables

**Process:**
1. Analyze annual usage of item
2. Negotiate annual contract with supplier
3. Issue blanket PO for 12 months
4. Release orders monthly/quarterly as needed
5. Review pricing and usage at contract renewal

## 7. Receiving and Inspection

### Incoming Inspection Checklist
- [ ] Verify part number matches PO and packing slip
- [ ] Check quantity received
- [ ] Inspect packaging for damage
- [ ] Verify manufacturer and country of origin (for critical parts)
- [ ] Check manufacturing date (reject if >6 months old for bearings)
- [ ] Inspect for physical damage, corrosion, contamination
- [ ] Verify dimensions with calipers (for precision parts)
- [ ] Review material certificates (if required)
- [ ] Match serial numbers (for traceable items)

### Acceptance Criteria
- Parts meet technical specifications
- No visible defects or damage
- Packaging intact and properly labeled
- Documentation complete (certs, test reports)
- Within acceptable manufacturing date range

### Rejection Process
If parts fail inspection:
1. Quarantine rejected parts (red tag, separate area)
2. Document defect with photos
3. Notify supplier within 48 hours
4. Request return authorization (RMA)
5. Return for credit or replacement
6. Follow up on replacement delivery

## 8. Storage and Preservation

### Storage Conditions

**Bearings:**
- Store in original packaging (greased and sealed)
- Horizontal position, small bearings; vertical, large bearings
- Temperature: 5-30°C, humidity <60% RH
- Rotate stock (FIFO - First In First Out)
- Shelf life: 2-3 years (grease degradation)
- Re-grease if stored >2 years

**Motors:**
- Store in dry, ventilated area
- Cover with plastic to prevent dust
- Rotate shaft monthly to prevent bearing flat spots
- Check insulation resistance before installation if stored >6 months
- Apply shaft rust preventive

**Belts:**
- Hang vertically or store flat (never fold or kink)
- Avoid direct sunlight (UV degradation)
- Temperature: 10-25°C
- Away from ozone sources (welding, motors)
- Shelf life: 3-5 years

**Seals and O-rings:**
- Store in sealed bags away from light
- Avoid compression or stretching
- Temperature: 15-25°C
- Check for hardening before use (should be flexible)
- Shelf life: 2-3 years (rubber degradation)

**Electrical Components:**
- Store in original anti-static packaging
- Dry environment (<50% humidity)
- Protect from dust and contamination
- Check for corrosion on contacts before use

### Warehouse Organization

**Location System:**
- Bin location coding: Zone-Aisle-Shelf-Bin (e.g., A-03-B-12)
- Barcode labels on all bins
- Critical spares in locked cage (controlled access)
- Fast-moving items near dispatch area
- Heavy items on lower shelves (safety)

**Kitting and Pre-Staging:**
- Create kits for common maintenance jobs
- Pre-stage parts for planned shutdowns
- Label kits clearly with equipment ID and job description

## 9. Inventory Tracking and Control

### Perpetual Inventory System
- Real-time update of stock levels
- Record every transaction (receipt, issue, return)
- Cycle counting to verify accuracy
- Target accuracy: >95%

### Cycle Counting Schedule
- **A-items**: Monthly (100% annually)
- **B-items**: Quarterly (100% annually)
- **C-items**: Semi-annually (100% annually)

**Process:**
1. Select items for count (by schedule or random)
2. Physical count without reference to system quantity
3. Compare count to system quantity
4. Investigate discrepancies >1 unit (A/B) or >5% (C)
5. Adjust system quantity and document reason

### Inventory Turnover Ratio
Measure inventory efficiency:

**Formula:**
```
Inventory Turnover = Annual Usage Value / Average Inventory Value
```

**Targets:**
- A-items: 2-4 turns per year (high value, low volume)
- B-items: 4-8 turns per year
- C-items: 8-12 turns per year (low value, high volume)

Low turnover → Overstocking, obsolescence risk
High turnover → Risk of stockouts, frequent ordering

## 10. Obsolescence Management

### Obsolescence Risk Factors
- Equipment nearing end of life (>15 years)
- Manufacturer discontinued product
- Technology superseded (old PLC models)
- Long shelf storage (>3 years unused)
- Changing plant configuration

### Annual Obsolescence Review
Identify slow-moving and obsolete items:
- No usage in past 24 months
- Equipment decommissioned
- Superseded by newer parts
- Shelf life expired

**Action Plan:**
1. Verify equipment status (active, standby, decommissioned)
2. Consult with reliability team on future needs
3. Decision matrix:
   - Keep: Critical spare for active equipment
   - Reduce stock: Lower quantity, monitor usage
   - Return to supplier: If within return period
   - Sell/liquidate: To other plants or third party
   - Scrap: If no value or unsafe

**Financial Impact:**
- Write-off obsolete inventory annually
- Adjust inventory valuation
- Prevent future over-purchasing

## 11. Performance Metrics (KPIs)

### Spare Parts KPIs
- **Stockout Rate**: <2% (percentage of requests not fulfilled from stock)
- **Inventory Accuracy**: >95% (cycle count accuracy)
- **Inventory Turnover**: 4-6 turns per year (overall)
- **Fill Rate**: >98% (orders fulfilled from existing stock)
- **Carrying Cost**: <20% of inventory value per year
- **Obsolescence Rate**: <3% of total inventory value per year
- **Emergency Orders**: <10% of total orders

### Monthly Reporting
- Total inventory value (by ABC classification)
- Stock adjustments (count discrepancies)
- Stockout incidents and impact
- Emergency procurements and reasons
- Slow-moving items (>12 months no usage)
- Top 10 items by usage value
- Vendor delivery performance

## 12. Continuous Improvement Initiatives

### Vendor-Managed Inventory (VMI)
For high-volume consumables:
- Vendor monitors stock levels
- Automatic replenishment when low
- Reduces administrative workload
- Improves availability
- Suitable for: grease, bolts, consumables

### Consignment Stock
For critical, high-value items:
- Supplier stores parts at customer site
- Customer pays only when used
- Improves availability, reduces cash tied up
- Suitable for: large motors, gearboxes

### Predictive Ordering
Use predictive maintenance data:
- RUL estimates trigger parts orders
- Align procurement with planned maintenance
- Reduce emergency orders
- Optimize lead time matching

### Supplier Integration
- Electronic data interchange (EDI) for orders
- Vendor portal for order status visibility
- Quality collaboration (reject rate reduction)
- Joint inventory optimization

## 13. Training and Competency

### Storekeeper Training
- Inventory management principles
- CMMS system operation
- Receiving and inspection procedures
- Storage and preservation methods
- Cycle counting procedures
- Safety (forklift, ladder, manual handling)

### Technician Training
- Spare parts identification and cross-referencing
- Self-service parts requisition
- Emergency parts location knowledge
- Proper handling of sensitive parts (bearings, electronics)

## 14. Documentation and Records

### Required Records (Retention: 5 years)
- Purchase orders and receiving documents
- Inspection reports and rejection records
- Inventory transaction history
- Cycle count reports
- Obsolescence review and write-off reports
- Supplier performance evaluations

## 15. Emergency Contacts

### Suppliers (24/7 Emergency Hotlines)
- SKF Bearings: +1-555-SKF-24HR
- ABB Motors: +1-555-ABB-HELP
- Electrical Distributor: +1-555-ELECTRIC

### Internal Contacts
- Spare Parts Manager: Ext. 2350
- Procurement Manager: Ext. 2351
- Stores Supervisor: Ext. 2355
- Emergency Parts Approval: Plant Manager Mobile

---

**Document Control:**
- Approved by: Maintenance Manager
- Next review date: February 2027
