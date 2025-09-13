"""
Bot Management System
Handles trading bot creation, configuration, and execution
"""

import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from enum import Enum
import threading
import queue

logger = logging.getLogger(__name__)

class BotType(Enum):
    DCA = "dollar_cost_averaging"
    MOMENTUM = "momentum_trading"
    MEAN_REVERSION = "mean_reversion"
    GRID = "grid_trading"
    ARBITRAGE = "arbitrage"
    NEWS = "news_based"
    TECHNICAL = "technical_analysis"

class BotStatus(Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    PAUSED = "paused"
    ERROR = "error"
    STOPPED = "stopped"

class TradingBot:
    def __init__(self, bot_id: int, user_id: int, name: str, bot_type: BotType, config: Dict[str, Any]):
        self.bot_id = bot_id
        self.user_id = user_id
        self.name = name
        self.bot_type = bot_type
        self.config = config
        self.status = BotStatus.INACTIVE
        self.performance_data = {}
        self.last_run = None
        self.trade_queue = queue.Queue()
        self.running = False
        
    def start(self):
        """Start the bot"""
        if self.status == BotStatus.ACTIVE:
            return {"success": False, "message": "Bot is already running"}
        
        self.status = BotStatus.ACTIVE
        self.running = True
        self.last_run = datetime.now()
        
        # Start bot thread
        bot_thread = threading.Thread(target=self._run_bot, daemon=True)
        bot_thread.start()
        
        return {"success": True, "message": "Bot started successfully"}
    
    def stop(self):
        """Stop the bot"""
        self.status = BotStatus.STOPPED
        self.running = False
        return {"success": True, "message": "Bot stopped successfully"}
    
    def pause(self):
        """Pause the bot"""
        self.status = BotStatus.PAUSED
        return {"success": True, "message": "Bot paused successfully"}
    
    def resume(self):
        """Resume the bot"""
        if self.status == BotStatus.PAUSED:
            self.status = BotStatus.ACTIVE
            return {"success": True, "message": "Bot resumed successfully"}
        return {"success": False, "message": "Bot is not paused"}
    
    def _run_bot(self):
        """Main bot execution loop"""
        while self.running and self.status == BotStatus.ACTIVE:
            try:
                if self.status == BotStatus.PAUSED:
                    time.sleep(1)
                    continue
                
                # Execute bot-specific logic
                if self.bot_type == BotType.DCA:
                    self._execute_dca_strategy()
                elif self.bot_type == BotType.MOMENTUM:
                    self._execute_momentum_strategy()
                elif self.bot_type == BotType.MEAN_REVERSION:
                    self._execute_mean_reversion_strategy()
                elif self.bot_type == BotType.GRID:
                    self._execute_grid_strategy()
                elif self.bot_type == BotType.NEWS:
                    self._execute_news_strategy()
                elif self.bot_type == BotType.TECHNICAL:
                    self._execute_technical_strategy()
                
                # Update last run time
                self.last_run = datetime.now()
                
                # Sleep based on config
                sleep_interval = self.config.get('sleep_interval', 60)  # Default 1 minute
                time.sleep(sleep_interval)
                
            except Exception as e:
                logger.error(f"Error in bot {self.bot_id}: {e}")
                self.status = BotStatus.ERROR
                break
    
    def _execute_dca_strategy(self):
        """Execute Dollar Cost Averaging strategy"""
        try:
            symbol = self.config.get('symbol')
            amount = self.config.get('amount', 100)
            interval_days = self.config.get('interval_days', 7)
            
            if not symbol:
                return
            
            # Check if it's time to buy
            last_trade = self._get_last_trade(symbol)
            if last_trade:
                days_since_last = (datetime.now() - last_trade['timestamp']).days
                if days_since_last < interval_days:
                    return
            
            # Execute buy order
            self._execute_trade(symbol, 'buy', amount)
            
        except Exception as e:
            logger.error(f"Error in DCA strategy: {e}")
    
    def _execute_momentum_strategy(self):
        """Execute Momentum Trading strategy"""
        try:
            symbol = self.config.get('symbol')
            lookback_period = self.config.get('lookback_period', 20)
            momentum_threshold = self.config.get('momentum_threshold', 0.02)
            
            if not symbol:
                return
            
            # Get price data (mock implementation)
            current_price = self._get_current_price(symbol)
            historical_prices = self._get_historical_prices(symbol, lookback_period)
            
            if len(historical_prices) < lookback_period:
                return
            
            # Calculate momentum
            momentum = (current_price - historical_prices[0]) / historical_prices[0]
            
            if momentum > momentum_threshold:
                # Strong upward momentum - buy
                amount = self.config.get('buy_amount', 100)
                self._execute_trade(symbol, 'buy', amount)
            elif momentum < -momentum_threshold:
                # Strong downward momentum - sell
                amount = self.config.get('sell_amount', 100)
                self._execute_trade(symbol, 'sell', amount)
            
        except Exception as e:
            logger.error(f"Error in momentum strategy: {e}")
    
    def _execute_mean_reversion_strategy(self):
        """Execute Mean Reversion strategy"""
        try:
            symbol = self.config.get('symbol')
            lookback_period = self.config.get('lookback_period', 20)
            deviation_threshold = self.config.get('deviation_threshold', 2.0)
            
            if not symbol:
                return
            
            # Get price data
            current_price = self._get_current_price(symbol)
            historical_prices = self._get_historical_prices(symbol, lookback_period)
            
            if len(historical_prices) < lookback_period:
                return
            
            # Calculate mean and standard deviation
            mean_price = sum(historical_prices) / len(historical_prices)
            variance = sum((x - mean_price) ** 2 for x in historical_prices) / len(historical_prices)
            std_dev = variance ** 0.5
            
            # Check if price is significantly above or below mean
            z_score = (current_price - mean_price) / std_dev
            
            if z_score > deviation_threshold:
                # Price is too high - sell
                amount = self.config.get('sell_amount', 100)
                self._execute_trade(symbol, 'sell', amount)
            elif z_score < -deviation_threshold:
                # Price is too low - buy
                amount = self.config.get('buy_amount', 100)
                self._execute_trade(symbol, 'buy', amount)
            
        except Exception as e:
            logger.error(f"Error in mean reversion strategy: {e}")
    
    def _execute_grid_strategy(self):
        """Execute Grid Trading strategy"""
        try:
            symbol = self.config.get('symbol')
            grid_size = self.config.get('grid_size', 10)
            grid_spacing = self.config.get('grid_spacing', 0.01)  # 1%
            base_price = self.config.get('base_price')
            
            if not symbol or not base_price:
                return
            
            current_price = self._get_current_price(symbol)
            
            # Calculate grid levels
            grid_levels = []
            for i in range(-grid_size//2, grid_size//2 + 1):
                level = base_price * (1 + i * grid_spacing)
                grid_levels.append(level)
            
            # Find closest grid level
            closest_level = min(grid_levels, key=lambda x: abs(x - current_price))
            level_index = grid_levels.index(closest_level)
            
            # Execute trades based on grid position
            if level_index < len(grid_levels) // 2:
                # Price is below middle - buy
                amount = self.config.get('grid_amount', 50)
                self._execute_trade(symbol, 'buy', amount)
            elif level_index > len(grid_levels) // 2:
                # Price is above middle - sell
                amount = self.config.get('grid_amount', 50)
                self._execute_trade(symbol, 'sell', amount)
            
        except Exception as e:
            logger.error(f"Error in grid strategy: {e}")
    
    def _execute_news_strategy(self):
        """Execute News-based strategy"""
        try:
            symbol = self.config.get('symbol')
            sentiment_threshold = self.config.get('sentiment_threshold', 0.7)
            
            if not symbol:
                return
            
            # Get news sentiment (mock implementation)
            sentiment = self._get_news_sentiment(symbol)
            
            if sentiment > sentiment_threshold:
                # Positive sentiment - buy
                amount = self.config.get('buy_amount', 100)
                self._execute_trade(symbol, 'buy', amount)
            elif sentiment < -sentiment_threshold:
                # Negative sentiment - sell
                amount = self.config.get('sell_amount', 100)
                self._execute_trade(symbol, 'sell', amount)
            
        except Exception as e:
            logger.error(f"Error in news strategy: {e}")
    
    def _execute_technical_strategy(self):
        """Execute Technical Analysis strategy"""
        try:
            symbol = self.config.get('symbol')
            indicators = self.config.get('indicators', ['rsi', 'macd', 'sma'])
            
            if not symbol:
                return
            
            # Get technical indicators (mock implementation)
            technical_data = self._get_technical_indicators(symbol, indicators)
            
            # Simple strategy based on RSI
            if 'rsi' in technical_data:
                rsi = technical_data['rsi']
                if rsi < 30:  # Oversold
                    amount = self.config.get('buy_amount', 100)
                    self._execute_trade(symbol, 'buy', amount)
                elif rsi > 70:  # Overbought
                    amount = self.config.get('sell_amount', 100)
                    self._execute_trade(symbol, 'sell', amount)
            
        except Exception as e:
            logger.error(f"Error in technical strategy: {e}")
    
    def _execute_trade(self, symbol: str, action: str, amount: float):
        """Execute a trade"""
        try:
            # Mock trade execution
            current_price = self._get_current_price(symbol)
            quantity = amount / current_price if action == 'buy' else amount
            
            trade_data = {
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'price': current_price,
                'timestamp': datetime.now(),
                'status': 'executed'
            }
            
            # Add to trade queue
            self.trade_queue.put(trade_data)
            
            # Update performance data
            self._update_performance_data(trade_data)
            
            logger.info(f"Bot {self.bot_id} executed {action} {quantity} {symbol} at {current_price}")
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
    
    def _get_current_price(self, symbol: str) -> float:
        """Get current price for symbol (mock implementation)"""
        # This would integrate with your price data system
        return 100.0  # Mock price
    
    def _get_historical_prices(self, symbol: str, period: int) -> List[float]:
        """Get historical prices (mock implementation)"""
        # This would integrate with your historical data system
        return [100.0] * period  # Mock data
    
    def _get_last_trade(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get last trade for symbol (mock implementation)"""
        # This would query the database
        return None
    
    def _get_news_sentiment(self, symbol: str) -> float:
        """Get news sentiment for symbol (mock implementation)"""
        # This would integrate with news analysis
        return 0.0  # Neutral sentiment
    
    def _get_technical_indicators(self, symbol: str, indicators: List[str]) -> Dict[str, float]:
        """Get technical indicators (mock implementation)"""
        # This would integrate with technical analysis
        return {'rsi': 50.0, 'macd': 0.0, 'sma': 100.0}
    
    def _update_performance_data(self, trade_data: Dict[str, Any]):
        """Update bot performance data"""
        if 'total_trades' not in self.performance_data:
            self.performance_data['total_trades'] = 0
            self.performance_data['total_volume'] = 0.0
            self.performance_data['profit_loss'] = 0.0
        
        self.performance_data['total_trades'] += 1
        self.performance_data['total_volume'] += trade_data['quantity'] * trade_data['price']
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get bot performance summary"""
        return {
            'bot_id': self.bot_id,
            'name': self.name,
            'bot_type': self.bot_type.value,
            'status': self.status.value,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'performance': self.performance_data
        }

class BotManager:
    def __init__(self, user_manager):
        self.user_manager = user_manager
        self.active_bots = {}  # bot_id -> TradingBot instance
        self.bot_configs = {
            BotType.DCA: {
                'symbol': 'BTC-USD',
                'amount': 100,
                'interval_days': 7,
                'sleep_interval': 3600  # 1 hour
            },
            BotType.MOMENTUM: {
                'symbol': 'AAPL',
                'lookback_period': 20,
                'momentum_threshold': 0.02,
                'buy_amount': 100,
                'sell_amount': 100,
                'sleep_interval': 300  # 5 minutes
            },
            BotType.MEAN_REVERSION: {
                'symbol': 'SPY',
                'lookback_period': 20,
                'deviation_threshold': 2.0,
                'buy_amount': 100,
                'sell_amount': 100,
                'sleep_interval': 300
            },
            BotType.GRID: {
                'symbol': 'ETH-USD',
                'grid_size': 10,
                'grid_spacing': 0.01,
                'base_price': 2000.0,
                'grid_amount': 50,
                'sleep_interval': 1800  # 30 minutes
            },
            BotType.NEWS: {
                'symbol': 'TSLA',
                'sentiment_threshold': 0.7,
                'buy_amount': 100,
                'sell_amount': 100,
                'sleep_interval': 600  # 10 minutes
            },
            BotType.TECHNICAL: {
                'symbol': 'NVDA',
                'indicators': ['rsi', 'macd', 'sma'],
                'buy_amount': 100,
                'sell_amount': 100,
                'sleep_interval': 300
            }
        }
    
    def create_bot(self, user_id: int, name: str, bot_type: str, custom_config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new trading bot"""
        try:
            # Validate bot type
            try:
                bot_type_enum = BotType(bot_type)
            except ValueError:
                return {"success": False, "message": f"Invalid bot type: {bot_type}"}
            
            # Get default config and merge with custom config
            config = self.bot_configs.get(bot_type_enum, {}).copy()
            if custom_config:
                config.update(custom_config)
            
            # Create bot in database
            result = self.user_manager.create_bot(user_id, name, bot_type, config)
            if not result['success']:
                return result
            
            bot_id = result['bot_id']
            
            # Create bot instance
            bot = TradingBot(bot_id, user_id, name, bot_type_enum, config)
            self.active_bots[bot_id] = bot
            
            return {"success": True, "bot_id": bot_id, "message": "Bot created successfully"}
            
        except Exception as e:
            logger.error(f"Error creating bot: {e}")
            return {"success": False, "message": f"Bot creation failed: {str(e)}"}
    
    def start_bot(self, bot_id: int) -> Dict[str, Any]:
        """Start a bot"""
        try:
            if bot_id not in self.active_bots:
                return {"success": False, "message": "Bot not found"}
            
            bot = self.active_bots[bot_id]
            result = bot.start()
            
            if result['success']:
                # Update database
                self.user_manager.update_bot_status(bot_id, 'active')
            
            return result
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            return {"success": False, "message": f"Failed to start bot: {str(e)}"}
    
    def stop_bot(self, bot_id: int) -> Dict[str, Any]:
        """Stop a bot"""
        try:
            if bot_id not in self.active_bots:
                return {"success": False, "message": "Bot not found"}
            
            bot = self.active_bots[bot_id]
            result = bot.stop()
            
            if result['success']:
                # Update database
                self.user_manager.update_bot_status(bot_id, 'stopped')
            
            return result
            
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            return {"success": False, "message": f"Failed to stop bot: {str(e)}"}
    
    def pause_bot(self, bot_id: int) -> Dict[str, Any]:
        """Pause a bot"""
        try:
            if bot_id not in self.active_bots:
                return {"success": False, "message": "Bot not found"}
            
            bot = self.active_bots[bot_id]
            result = bot.pause()
            
            if result['success']:
                # Update database
                self.user_manager.update_bot_status(bot_id, 'paused')
            
            return result
            
        except Exception as e:
            logger.error(f"Error pausing bot: {e}")
            return {"success": False, "message": f"Failed to pause bot: {str(e)}"}
    
    def resume_bot(self, bot_id: int) -> Dict[str, Any]:
        """Resume a bot"""
        try:
            if bot_id not in self.active_bots:
                return {"success": False, "message": "Bot not found"}
            
            bot = self.active_bots[bot_id]
            result = bot.resume()
            
            if result['success']:
                # Update database
                self.user_manager.update_bot_status(bot_id, 'active')
            
            return result
            
        except Exception as e:
            logger.error(f"Error resuming bot: {e}")
            return {"success": False, "message": f"Failed to resume bot: {str(e)}"}
    
    def get_bot_performance(self, bot_id: int) -> Dict[str, Any]:
        """Get bot performance data"""
        try:
            if bot_id not in self.active_bots:
                return {"success": False, "message": "Bot not found"}
            
            bot = self.active_bots[bot_id]
            return {"success": True, "performance": bot.get_performance_summary()}
            
        except Exception as e:
            logger.error(f"Error getting bot performance: {e}")
            return {"success": False, "message": f"Failed to get performance: {str(e)}"}
    
    def get_available_bot_types(self) -> List[Dict[str, str]]:
        """Get list of available bot types"""
        return [
            {"value": bot_type.value, "name": bot_type.value.replace('_', ' ').title()}
            for bot_type in BotType
        ]
    
    def get_bot_config_template(self, bot_type: str) -> Dict[str, Any]:
        """Get configuration template for a bot type"""
        try:
            bot_type_enum = BotType(bot_type)
            return self.bot_configs.get(bot_type_enum, {})
        except ValueError:
            return {}

# Initialize bot manager
from enhanced_user_management import enhanced_user_manager
bot_manager = BotManager(enhanced_user_manager)
