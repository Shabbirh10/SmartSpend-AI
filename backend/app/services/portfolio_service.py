import yfinance as yf
from app.models import db, Investment
import sqlalchemy as sa
from sqlalchemy.future import select

async def get_portfolio_summary():
    """Fetches all investments and their current market data using yfinance."""
    from app.models import async_session
    async with async_session() as session:
        result = await session.execute(select(Investment))
        investments = result.scalars().all()

    portfolio = []
    total_value = 0.0
    total_cost = 0.0

    if not investments:
        return {
            "holdings": [],
            "summary": { "total_value": 0, "total_cost": 0, "total_unrealized_pl": 0, "total_pl_percent": 0 }
        }

    # Bulk fetch using yf.download (one network request)
    tickers_list = [inv.ticker for inv in investments]
    price_map = {}
    try:
        # Download 1 day of data for all tickers with strict timeout
        data = yf.download(" ".join(tickers_list), period="1d", group_by="ticker", threads=True, progress=False, timeout=2.0)
        for ticker in tickers_list:
            try:
                # Handle single ticker vs multiple tickers response format
                if len(tickers_list) == 1:
                    last_price = data['Close'].iloc[-1]
                else:
                    last_price = data[ticker]['Close'].iloc[-1]
                price_map[ticker] = float(last_price)
            except Exception:
                price_map[ticker] = None
    except Exception as e:
        print(f"yfinance bulk download failed: {e}")

    import math

    def sanitize(val):
        if val is None or math.isnan(val):
            return 0.0
        return float(val)

    for inv in investments:
        current_price = price_map.get(inv.ticker)
        if current_price is None or math.isnan(current_price):
            current_price = inv.average_price

        current_price = sanitize(current_price)
        market_value = inv.shares * current_price
        cost_basis = inv.shares * inv.average_price
        unrealized_pl = market_value - cost_basis
        pl_percent = (unrealized_pl / cost_basis * 100) if cost_basis > 0 else 0

        total_value += market_value
        total_cost += cost_basis

        portfolio.append({
            "id": inv.id,
            "ticker": inv.ticker,
            "shares": sanitize(inv.shares),
            "average_price": sanitize(inv.average_price),
            "current_price": round(current_price, 2),
            "market_value": round(market_value, 2),
            "unrealized_pl": round(unrealized_pl, 2),
            "pl_percent": round(pl_percent, 2)
        })

    total_unrealized_pl = total_value - total_cost
    total_pl_percent = (total_unrealized_pl / total_cost * 100) if total_cost > 0 else 0

    return {
        "holdings": portfolio,
        "summary": {
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "total_unrealized_pl": round(total_unrealized_pl, 2),
            "total_pl_percent": round(total_pl_percent, 2)
        }
    }

async def add_investment(ticker: str, shares: float, price: float):
    from app.models import async_session
    async with async_session() as session:
        result = await session.execute(select(Investment).where(Investment.ticker == ticker))
        inv = result.scalar_one_or_none()

        if inv:
            # Update average price and shares
            total_cost = (inv.shares * inv.average_price) + (shares * price)
            inv.shares += shares
            inv.average_price = total_cost / inv.shares
        else:
            inv = Investment(ticker=ticker, shares=shares, average_price=price)
            session.add(inv)
        
        await session.commit()
        return inv.to_dict()
